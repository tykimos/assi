import os
# Use the package we installed
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

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
                    "text": "*어시 홈에 방문해주셔서 감사드려요~* :tada:"
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
    
# Listens to incoming messages that contain "hello"
@app.message("휴가")
def message_hg(message, say):

  recv_msg = message['text']

  if recv_msg.count(' ') == 2:
    msg_data = recv_msg.split()

    say(text = f"(테스트중) {msg_data[1]}에 {msg_data[2]}(으)로 휴가 신청이 잘 접수되었습니다. <@{message['user']}>님 이 날 만큼은 푹 쉬세요~")

  else:
    say(text = f"휴가 신청 양식(날짜 타입)이 다릅니다. '휴가 210414 오전반차' 또는 '휴가 210414 오후반차' 또는 '휴가 210414 종일'으로 입력해주세요.")

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

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))