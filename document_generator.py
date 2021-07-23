#!/usr/bin/env python
# coding: utf-8

#-*- encoding: utf-8 -*-

# 필요한 패키지를 가져옵니다.

import json
import datetime
import threading
import os

from PIL import Image, ImageFont, ImageDraw
import pandas as pd
import numpy as np
from img2pdf import convert
import csv
import uuid

fontpath = '/Library/Fonts/NanumBarunGothic.ttf'

checking_period = 10 #secs

wo_wait_dir = "wo/wait/"
wo_running_dir = "wo/running/"
wo_success_dir = "wo/success/"
wo_fail_dir = "wo/fail/"
wo_warehouse_dir = 'wo/warehouse/'
wo_temp_dir = 'wo/temp/'
form_dir = 'form/'

def wo_from_json(wo_filename):
    wo = None
    with open(wo_running_dir + wo_filename, "rt", encoding='utf-8') as json_file:
        wo = json.load(json_file)
    return wo

def content_from_wo(wo, wo_filename):
    
    contract_name = wo["contract_name"]

    wo_filepath = wo_running_dir + wo_filename
    content_filepath = wo_temp_dir + wo_filename + '.with_content.csv'

    cmd = 'python ' + form_dir + contract_name + '.py ' + wo_filepath + ' ' + content_filepath
    os.system(cmd)

    cf = open(content_filepath, 'rt')
    reader = csv.reader(cf, delimiter=',')
    content = list(reader)
    
    return content[0]

def pdf_from_content(wo, content, pdf_filename):
    
    contract_name = wo["contract_name"]

    # 양식 및 콘텐츠 데이터를 로딩합니다.
    form_meta = pd.read_csv(form_dir + contract_name + '.csv', skipinitialspace=True)
    form_img = Image.open(form_dir + contract_name + '.png')
    
    # 콘텐츠 정보로 양식 채워 이미지로 저장합니다.
    draw_img = ImageDraw.Draw(form_img)

    for idx, row in form_meta.iterrows():

        x_pos = int(row[1])
        y_pos = int(row[2]) + 3
        font_size = int(row[3] * 1.8)
        str_text = content[idx]
        img_font = ImageFont.truetype(fontpath, font_size)
        draw_img.text((x_pos, y_pos), str_text, fill='black', font=img_font)

    form_pdf = form_img.convert('RGB')
    form_pdf.save(wo_warehouse_dir + pdf_filename)

def on_check_wo():

    for wo_filename in os.listdir(wo_wait_dir):
        if wo_filename.startswith('create_document'):

            os.rename(wo_wait_dir+wo_filename, wo_running_dir+wo_filename)
            print("move wo to running. ", wo_filename)

            wo = wo_from_json(wo_filename)
            content = content_from_wo(wo, wo_filename)

            pdf_filename = uuid.uuid4().hex[:8] + '_' + wo["contract_name"] + '_' + wo["subject"] + '.pdf'
            pdf_from_content(wo, content, pdf_filename)
            
            os.rename(wo_running_dir+wo_filename, wo_success_dir+wo_filename)
            print("move wo to success. ", wo_filename)

def on_timer():
    print('check send slack wo at ' + str(datetime.datetime.now()))
    on_check_wo()
    timer = threading.Timer(checking_period, on_timer)
    timer.start()

if __name__ == "__main__":
    on_timer()