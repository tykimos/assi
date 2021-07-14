# 필요한 패키지를 가져옵니다.

import json
import datetime
import threading
import os

from PIL import Image, ImageFont, ImageDraw
import pandas as pd
import numpy as np
from img2pdf import convert

fontpath = '/Library/Fonts/NanumBarunGothic.ttf'

checking_period = 10 #secs

wo_wait_dir = "wo/wait/"
wo_running_dir = "wo/running/"
wo_success_dir = "wo/success/"
wo_fail_dir = "wo/fail/"
wo_warehouse_dir = 'wo/warehouse/'

# 양식 및 콘텐츠 데이터를 로딩합니다.
form_meta = pd.read_csv('form_meta.csv', skipinitialspace=True)
contents = pd.read_csv('contents.csv', skipinitialspace=True, header=None)

# 콘텐츠 정보로 양식 채워 이미지로 저장합니다.
for c_idx, c_row in contents.iterrows():
    form_img = Image.open('form.png')
    draw_img = ImageDraw.Draw(form_img)

    for fm_idx, fm_row in form_meta.iterrows():

        x_pos = int(fm_row[1])
        y_pos = int(fm_row[2])
        font_size = int(fm_row[3] * 1.8)
        str_text = str(c_row[fm_idx+1])

        img_font = ImageFont.truetype(fontpath, font_size)
        draw_img.text((x_pos, y_pos), str_text, fill='black', font=img_font)
    
    output_filename = c_row[0] + '_' + c_row[1] + '.pdf'
    form_pdf = form_img.convert('RGB')
    form_pdf.save(output_filename)

'''
{
        "doc_type" : "contract",
        "contract_name" : "연봉계약서",
        "subject" : "홍길동",
        "period" : "2022년 1월 1일/2022년 12월 30일/12개월",
        "salary" : "50,000,000원",
        "payment_date" : "15일",
        "contract_date" : "2021년 12월 30일",
        "signatories" : "김태영(tykim@aifactory.page), 홍길동(adam.tykim@gmail.com)"
}
'''

def wo_from_json(filepath):
    wo = None
    with open(filepath, "rt", encoding='utf-8') as json_file:
        wo = json.load(json_file)
    return wo

def content_from_wo(wo):
    
    content = []
    content.append('(주)인공지능팩토리')
    content.append(wo["subject"])

    period = wo["period"].split('/')

    content.append(period[0])
    content.append(period[1])
    content.append(period[2])

    content.append(wo["salary"])
    content.append(wo["payment_date"])
    content.append(wo["contract_date"])

    signatories = wo["signatories"].split(',')


    wo['doc_type']
        "contract_name" : "연봉계약서",
        "subject" : "홍길동",
        "period" : "2022년 1월 1일/2022년 12월 30일/12개월",
        "salary" : "50,000,000원",
        "payment_date" : "15일",
        "contract_date" : "2021년 12월 30일",
        "signatories" : "김태영(tykim@aifactory.page), 홍길동(adam.tykim@gmail.com)"

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

    content =''
    return content

def pdf_from_content(content):
    pass

def on_check_wo():

    for filename in os.listdir(wo_wait_dir):
        if filename.startswith('create_document'):

            os.rename(wo_wait_dir+filename, wo_running_dir+filename)
            print("move wo to running. ", filename)

            wo = wo_from_json(wo_wait_dir + filename)
            content = content_from_wo(wo)
            pdf_from_content(content, wo['contract_name'])            
            
            os.rename(wo_running_dir+filename, wo_success_dir+filename)
            print("move wo to success. ", filename)

def on_timer():
    print('check create document wo at ' + str(datetime.datetime.now()))
    on_check_wo()
    timer = threading.Timer(checking_period, on_timer)
    timer.start()

if __name__ == "__main__":
    on_timer()