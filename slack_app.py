# -*- coding: utf-8 -*-

import os
# Use the package we installed
from slack_bolt import App
import sqlite3
import datetime
import pandas as pd
import logging

checking_period = 10 #secs

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

from slack_sdk.errors import SlackApiError

# WebClient insantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
logger = logging.getLogger(__name__)

# Add functionality here
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
            "type": "home",
            "callback_id": "home_view",

            # body of the view
            "blocks": [
                {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*어시 홈에 방문해주셔서 감사드려요~* v001:tada:"
                }
                },
                {
                "type": "divider"
                },
                {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "하시는 일에 집중하고 즐길 수 있도록 제가 열심히 어시시트 해드릴께요~ 사용법 >> https://www.notion.so/aifactory/0482af8e47b84abc939aa5542956546d"
                }
                }
            ]
            }
        )

    except Exception as e:
        logger.error("Error publishing home tab:")


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


def db_hg_proc(user_id, reg_dt, hg_dt, hg_type):
  dbcon = sqlite3.connect("af_admin.db")
  raw_data = {'user_id': [user_id], 'reg_dt': [reg_dt], 'hg_dt':[hg_dt], 'hg_type':[hg_type]}
  df = pd.DataFrame(raw_data)
  df.to_sql('hg_proc', dbcon, if_exists='append', index_label='index')
  dbcon.commit()
  dbcon.close()


# Listens to incoming messages that contain "hello"
@app.message("휴가")
def message_hg(message, say):

  recv_msg = message['text']

  if recv_msg.count(' ') == 2:
    msg_data = recv_msg.split()

    say(text = f"(테스트중) {msg_data[1]}에 {msg_data[2]}(으)로 휴가 신청이 잘 접수되었습니다. <@{message['user']}>님 이 날 만큼은 푹 쉬세요~")

    db_hg_proc(message['user'], datetime.datetime.now().strftime("%Y%m%d%H%M%S"), msg_data[1], msg_data[2])

  else:
    say(text = f"휴가 신청 양식(날짜 타입)이 다릅니다. '휴가 20210414 오전반차' 또는 '휴가 20210414 오후반차' 또는 '휴가 20210414 종일'으로 입력해주세요.")

'''
@app.message("법카")
def message_bc(message, say):

  recv_msg = message['text']

  if recv_msg.count(' ') == 5:
    msg_data = recv_msg.split()

    say(text = f"(테스트중) {msg_data[1]}에 {msg_data[2]} 관련 {msg_data[3]}({msg_data[4]})(으)로 법카 {msg_data[5]}원 사용 보고가 잘 접수되었습니다. <@{message['user']}>님 고생 많으셨어요~")

  else:
    say(text = f"법카 사용 보고 양식(날짜 사업 비목 상세 금액)이 다릅니다. '법카 210414 전시회 톨비 대전>서울 10000' 또는 '법카 210414 공통 점심 김태영,홍길동 10000' 또는 '법카 210414 KT 회의 김태영 10000'으로 입력해주세요.")

@app.message("입체금")
def message_icg(message, say):
  recv_msg = message['text']

  if recv_msg.count(' ') == 5:
    msg_data = recv_msg.split()

    say(text = f"(테스트중) {msg_data[1]}에 {msg_data[2]} 관련 {msg_data[3]}({msg_data[4]})(으)로 입체금 {msg_data[5]}원 청구가 잘 접수되었습니다. <@{message['user']}>님 고생 많으셨어요~")

  else:
    say(text = f"입체금 청구 양식(날짜 사업 비목 상세 금액)이 다릅니다. '입체금 210414 전시회 톨비 대전>서울 10000' 또는 '입체금 210414 일반 점심 김태영,홍길동 10000' 또는 '입체금 210414 KT 회의 김태영 10000'으로 입력해주세요.")
'''

@app.message("로또")
def message_icg(message, say):
  import random
  num = str(sorted(random.sample(range(1,46) ,6)))
  say(text = f"행운이 깃든 숫자들입니다! {num}")

@app.message("양식")
def message_request(message, say):
  blocks = [
    {
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "제가 준비한 양식들이예요~",
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "법카사용신청"
					},
					"url": "https://forms.gle/STUPHjUbBr2atB5FA",
					"value": "click_me_123",
					"action_id": "actionId-0"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "입체금신청"
					},
					"url": "https://forms.gle/4uQ6bNbEjCVBDV1u8",
					"value": "click_me_123",
					"action_id": "actionId-1"
				}
			]
		}
  ]

  say(blocks=blocks, text = f"제가 받을 수 있는 양식들이예요~")

import threading


wo_wait_dir = "wo/wait/"
wo_running_dir = "wo/running/"
wo_success_dir = "wo/success/"
wo_fail_dir = "wo/fail/"
wo_warehouse_dir = 'wo/warehouse/'
wo_temp_dir = 'wo/temp/'

import json # import json module

# Channel you want to post message to

def get_channel_id(user_account):
  if user_account == 'tykim@aifactory.page':
    return 'U01C6C97E4S'
  return None

'''
def temp():
    
    print('check slack wo at ' + str(datetime.datetime.now()))

    files = os.listdir(slack_wait_dir)

    for filename in files:
        
        print(filename) # SMS_20210614210339_1.wo
        
        os.rename(slack_wait_dir+filename, slack_running_dir+filename)
        print("move wo to running. ", filename)

        # with statement
        with open(slack_running_dir+filename, "rt", encoding='utf-8') as json_file:

          json_data = json.load(json_file)

          print(json_data)
          
          channel_id = get_channel_id(json_data['user'])
          if channel_id is not None:

            if 'CARD' in str(filename):
            
              text_msg = f"법카 {json_data['time']} {json_data['type']} {json_data['card']} {json_data['amount']} {json_data['note']}"
              
              try:
                # Call the chat.scheduleMessage method using the WebClient
                result = app.client.chat_postMessage(
                    channel=channel_id,
                    text=text_msg
                )
                # Log the result
                logger.info(result)
              except SlackApiError as e:
                  logger.error("Error scheduling message: {}".format(e))

            elif 'DOC' in str(filename):
              
              text_msg = f"{json_data['docname']} 관련 문서 처리가 완료되었습니다. 문서명 : {json_data['filename']}"
              
              try:
                # Call the chat.scheduleMessage method using the WebClient
                result = app.client.chat_postMessage(
                    channel=channel_id,
                    text=text_msg
                )
                # Log the result
                logger.info(result)
              except SlackApiError as e:
                  logger.error("Error scheduling message: {}".format(e))

            os.rename(slack_running_dir+filename, slack_success_dir+filename)
            print("move wo to success. ", filename)
      
    timer = threading.Timer(5, startTimer)
    timer.start()
'''

def on_plain_text(wo, timestamp):
  
  text_msg = f"{json_data['docname']} 관련 문서 처리가 완료되었습니다. 문서명 : {json_data['filename']}"

  channel_id = get_channel_id(json_data['user'])

  try:
    # Call the chat.scheduleMessage method using the WebClient
    result = app.client.chat_postMessage(
      channel=channel_id,
      text=text_msg
    )
    # Log the result
    logger.info(result)
  except SlackApiError as e:
    logger.error("Error message: {}".format(e))

def wo_proc(wo):

    # 메시지 처리
    timestamp = datetime.datetime.today()

    print('MSG PROC : ' + wo['type'])

    if wo['type'] == "plain_text":
          on_plain_text(wo, timestamp)

def wo_from_json(wo_filename):
    wo = None
    with open(wo_running_dir + wo_filename, "rt", encoding='utf-8') as json_file:
        wo = json.load(json_file)
    return wo

def on_check_wo():
    
    for wo_filename in os.listdir(wo_wait_dir):
        if wo_filename.startswith('send_slack'):

            os.rename(wo_wait_dir+wo_filename, wo_running_dir+wo_filename)
            print("move wo to running. ", wo_filename)

            wo = wo_from_json(wo_filename)
            wo_proc(wo)
            
            os.rename(wo_running_dir+wo_filename, wo_success_dir+wo_filename)
            print("move wo to success. ", wo_filename)

def on_timer():
    print('check send slack wo at ' + str(datetime.datetime.now()))
    on_check_wo()
    timer = threading.Timer(checking_period, on_timer)
    timer.start()

# Start your app
if __name__ == "__main__":
    on_timer()
    app.start(port=int(os.environ.get("PORT", 3000)))