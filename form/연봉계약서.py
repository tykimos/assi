# 필요한 패키지를 가져옵니다.
import sys
import json
import csv

wo_fn = sys.argv[1]
content_fn = sys.argv[2]

with open(wo_fn, "rt", encoding='utf-8') as wo_file:
    wo = json.load(wo_file)

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

signatories = wo["signatories"].replace(' ', '').split(',')

content.append(signatories[0].split('(')[0])
content.append(signatories[1].split('(')[0])

with open(content_fn, 'wt') as content_file:
    write = csv.writer(content_file) 
    write.writerow(content)