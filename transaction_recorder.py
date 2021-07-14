#-*- encoding: utf-8 -*-

import json
import pygsheets
import datetime
import os

from pydrive.drive import GoogleDrive


db_wait_dir = "wo/db/wait/"
db_running_dir = "wo/db/running/"
db_success_dir = "wo/db/success/"
db_fail_dir = "wo/db/fail/"
db_warehouse_dir = "wo/db/warehouse/"

slack_wait_dir = "wo/slack/wait/"
slack_running_dir = "wo/slack/running/"
slack_success_dir = "wo/slack/success/"
slack_fail_dir = "wo/slack/fail/"

gc = pygsheets.authorize(outh_file='client_secret_346332774611-45shmna49816qabn40254fbbgm0pfphn.apps.googleusercontent.com.json')

prev_time_str = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
count_index = 0

from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

def upload_to_gdrive(filename, filepath):
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({'title':filename, 'mimeType':'application/pdf'})
    file1.SetContentFile(filepath)
    file1.Upload() # Update content of the file.

    print('title: %s, id: %s' % (file1['title'], file1['id']))

def get_wo_id(prefix):
    global prev_time_str
    global count_index
    curr_time_str = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    
    if curr_time_str == prev_time_str:
        count_index = count_index + 1
    else:
        count_index = 0
        prev_time_str = curr_time_str
    
    wo_id = prefix + '_' + curr_time_str + '_' + str(count_index) + '.wo'
    
    return wo_id

def generate_slack_card_wo(record):
    filename = slack_wait_dir + get_wo_id('CARD')
    with open(filename, 'w', encoding="utf-8") as fp:
        json.dump(record, fp, ensure_ascii=False)

def generate_slack_doc_wo(record):
    filename = slack_wait_dir + get_wo_id('DOC')
    with open(filename, 'w', encoding="utf-8") as fp:
        json.dump(record, fp, ensure_ascii=False)

def insert_card_sheet(record):
    file_name = record['user']
    sh_file = gc.open(file_name)
    sheet = sh_file.sheet1
    cells = sheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    last_row = len(cells)
    new_row = [ record['type'], record['card'], record['amount'], record['note'] ]    
    worksheet = sheet.insert_rows(last_row, number=1, values= new_row)

def insert_doc_sheet(record):
    file_name = 'contract_document'
    sh_file = gc.open(file_name)
    sheet = sh_file.sheet1
    cells = sheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    last_row = len(cells)
    new_row = [ record['user'], record['docname'], record['filename'], record['time'] ]    
    worksheet = sheet.insert_rows(last_row, number=1, values= new_row)

def db_wo_check():
    
    files = os.listdir(db_wait_dir)

    for filename in files:
        
        print(filename) # SMS_20210614210339_1.wo
        
        os.rename(db_wait_dir+filename, db_running_dir+filename)
        print("move wo to running. ", filename)

        # with statement
        with open(db_running_dir+filename, "rt", encoding='utf-8') as json_file:

            json_data = json.load(json_file)

            print(json_data)

            db_text = json_data["text"]
            db_from = json_data["from"]
            db_time = json_data["time"]
            db_name = json_data["name"]

            if db_text.find('신한') >= 0 & db_text.find('6764'):
                texts = db_text.split(' ')        

                record = {}
                record['user'] = 'tykim@aifactory.page'
                record['time'] = db_time
                record['type'] = texts[1]
                record['card'] = texts[2]
                record['amount'] = texts[5]
                record['note'] = " ".join(texts[6:])

                insert_card_sheet(record)
                generate_slack_card_wo(record)
            elif db_text.find('[개별공지]') >= 0:

                record = {}
                record['user'] = db_from
                record['time'] = db_time
                record['docname'] = db_text
                record['filename'] = db_name

                insert_doc_sheet(record)
                upload_to_gdrive(db_name, db_warehouse_dir + db_name)
                generate_slack_doc_wo(record)
            else:
                print('no match')
            
        os.rename(db_running_dir+filename, db_success_dir+filename)
        print("move wo to success. ", filename)

import threading

def startTimer():
    
    print('check email wo at ' + str(datetime.datetime.now()))

    db_wo_check()

    timer = threading.Timer(5, startTimer)
    timer.start()

if __name__ == "__main__":
    startTimer()