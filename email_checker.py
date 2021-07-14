#!/usr/bin/env python
# coding: utf-8

#-*- encoding: utf-8 -*-

import email
import imaplib
import html
import os
import json
import datetime
import threading
import base64

checking_period = 60*3
wo_wait_dir = "wo/wait/"
wo_running_dir = "wo/running/"
wo_success_dir = "wo/success/"
wo_fail_dir = "wo/fail/"
wo_warehouse_dir = 'wo/warehouse/'

# 이메일 받은편지함 계정 정보
email_account_file = 'email_account.json'

# 아래 메일에서 발송되는 wo만 수신합니다.
wo_vaild_sender = 'taeyoung.kim.ai@gmail.com'

'''
the content of the email_account_file is as following:
{
    "user" : "xxx@gmail.com",
    "password" : "xxx",
    "server" : "imap.gmail.com"
}
'''

def decode_with_charset(text):
    
    decoded_string, charset = email.header.decode_header(text)[0]

    decoded_text = ''

    if charset is not None:
        try:
            decoded_text = decoded_string.decode(charset)
        except UnicodeDecodeError:
            print("Cannot decode addr name " + decoded_string)
    else:
        decoded_text = decoded_string
    
    return decoded_text


def parseaddr_unicode(addr):

    from_name, from_email = email.utils.parseaddr(addr)
    from_email = from_email.strip().lower()

    if from_name:
        from_name = from_name.strip()
        from_name = decode_with_charset(from_name)

    return from_name, from_email 

def on_wo_received(msg_subject, message, timestamp):

    # wo 파일명 결정
    wo_filename = ''

    # [wo] 공백 다음의 문자열을 ID로 간주
    wo_id_start_index = msg_subject.find(' ') + 1
    wo_filename = msg_subject[wo_id_start_index:]

    # 완성되지 않은 wo이라면 정보 채움
    wo_filename = wo_filename.replace('{date}', timestamp.strftime('%Y%m%d%H%M%S'))
    wo_filename = wo_filename.replace('{seq}', timestamp.strftime('%f')[:-3])

    # 콘텐츠 가져오기
    content = ''

    if message.is_multipart():
        for part in message.walk():
            print(part)
            if part.get_content_type() == 'text/html':
                text = part.get_payload()
                text = html.unescape(text)
                content = text
                break
    else:
        content = message.get_payload()
        enc = message['Content-Transfer-Encoding']
        if enc == "base64":
            content = base64.b64decode(content).decode('utf-8')
                
    # wo 파일 저장
    with open(wo_wait_dir + wo_filename, 'wt') as fp:
        fp.write(content)
        fp.close()
        print(wo_filename + ' is generated.')

def on_sign_received(msg_from_name, msg_from_email, msg_subject, message, timestamp):
    
    str_idx = msg_subject.find('#')
    doc_id = msg_subject[str_idx:str_idx+8]

    attach_filename_postfix = '_' + msg_from_email + '_' + doc_id + '_' + timestamp.strftime('%Y%m%d%H%M%S') + '_' + timestamp.strftime('%f')[:-3]

    if message.is_multipart():
        for part in message.walk():

            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            decoded_attach_filename = decode_with_charset(part.get_filename())
            attach_filename = decoded_attach_filename + attach_filename_postfix

            # wo 파일 저장
            with open(wo_warehouse_dir + attach_filename, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
                fp.close()
                print(attach_filename + ' is generated.')

    wo = {}
    wo['document_id'] = doc_id
    wo['filename'] = attach_filename
    wo['from_name'] = msg_from_name
    wo['from_email'] = msg_from_email
    wo['timestamp'] = timestamp.strftime('%Y%m%d%H%M%S%f')[:-3]

    wo_filename = 'check_sign_' + timestamp.strftime('%Y%m%d%H%M%S') + '_' + timestamp.strftime('%f')[:-3] + '.wo'
    
    with open(wo_wait_dir + wo_filename, 'w', encoding="utf-8") as fp:
        json.dump(wo, fp, ensure_ascii=False)
        print(wo_filename + 'is generated')

def message_proc(message):

    # 메시지 디코딩
    msg_from_name, msg_from_email = parseaddr_unicode(message['from'])
    msg_subject = decode_with_charset(message['subject'])
    print('MSG PROC : ' + msg_from_name + ',' + msg_from_email + ',' + msg_subject)

    # 메시지 처리
    timestamp = datetime.datetime.today()

    if '[wo]' in msg_subject and msg_from_email == wo_vaild_sender:
        on_wo_received(msg_subject, message, timestamp)
    elif '[sign]' in msg_subject:
        on_sign_received(msg_from_name, msg_from_email, msg_subject, message, timestamp)
    
def on_check_inbox():

    # 이메일 계정 정보 json 파일 불러오기
    with open(email_account_file, "rt") as jsfp:
        account_info = json.load(jsfp)

    # 이메일 계정 연결하기
    mail = imaplib.IMAP4_SSL(account_info['server'])
    mail.login(account_info['user'], account_info['password'])
    
    # 받은편지함 선택
    mail.select('inbox')

    # 받은편지함에서 읽지 않은 메일 가져오기
    status, data = mail.search(None, '(UNSEEN)')

    print(status)
    print(data)

    # 메일 아이디 목록 구성하기 [b'1 2 3', b'4 5 6'] >> [b'1', b'2', b'3', b'4', b'5', b'6']
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    # 메일 아이디 순회하기
    for i in mail_ids:
        
        # 메일 아이디에 해당하는 메일 내용 가져오기
        status, data = mail.fetch(i, '(RFC822)')
        # 반환값 예시 : ('OK', [('1 (RFC822 {858569}', 'body of the message', ')')])

        for response_part in data:
            if isinstance(response_part, tuple):
                # 메일 데이터 가져오기
                message = email.message_from_bytes(response_part[1])
                # 메일 데이터 프로시저
                message_proc(message)

def on_timer():
    print('check email wo at ' + str(datetime.datetime.now()))
    on_check_inbox()
    timer = threading.Timer(checking_period, on_timer)
    timer.start()

if __name__ == "__main__":
    on_timer()

