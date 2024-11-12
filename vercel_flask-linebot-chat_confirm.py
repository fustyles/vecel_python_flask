"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3
"""

# 引入 Flask 框架及其相關模組
from flask import Flask, jsonify, request  
# 引入 http.client 模組，用於發送 HTTP 請求
import http.client  
# 引入 json 模組，用於處理 JSON 資料
import json

app = Flask(__name__)

# 設定專案標題
app.config['Project_title'] = '法蘭斯的ChatBot'

# Line Bot CHANNEL ACCESS TOKEN
CHANNEL_ACCESS_TOKEN = "iSHcOEyq3PM0Oe/PvgmCY69jAOdW6cWoj1Zn34VFgduEJzGlWWcZnAo6LjMt3L9EAldBB4erN2yt/E5tXQNQt7jSyOGKseY2jPD8czzI/RURL7jF/PBKtGm8PwIIymzXcqqdZLP2zaKRhliJUIMdJQdB04t89/1O/w1cDnyilFU=123"   

# 開關燈控制指令
app.config['confirm_list'] = {
    "開燈": 'on',
    "關燈": 'off'
}

# 定義一個路由 /about 觸發此函數
@app.route('/about')
def about():
    return app.config['Project_title']

# 定義一個路由 / 觸發此函數
@app.route("/", methods=['POST'])
def home():
    if request.method == 'POST':
        msg = request.get_json()        
        try:
            if msg and 'events' in msg and len(msg['events']) > 0:
                for event in msg['events']:
                    reply_token = event['replyToken']
                    # 回傳request資料 reply_message_to_line_bot(CHANNEL_ACCESS_TOKEN, reply_token, str(msg))
                    linebot_response = handle_event(event)
                    if linebot_response:
                        reply_message = [
                            {
                                'type': 'text',
                                'text': linebot_response
                            }
                        ]                    
                        reply_message_to_line_bot(CHANNEL_ACCESS_TOKEN, reply_token, reply_message)
                    
        except Exception as e:
            # 捕捉並回應錯誤訊息
            return jsonify({"data": msg, "error": str(e)}), 200
        
        return "OK", 200            

def reply_message_to_line_bot(access_token, reply_token, reply_message):
    host = 'api.line.me'
    endpoint = '/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'replyToken': reply_token,
        'messages': reply_message
    }

    # 建立 HTTP 連線
    conn = http.client.HTTPSConnection(host)
    
    # 發送 POST 請求
    conn.request("POST", endpoint, body=json.dumps(payload), headers=headers)
    
    # 獲取回應
    response = conn.getresponse()
    status_code = response.status
    conn.close()
    
    return status_code

def handle_event(event): 
    event_type = event['type']
                
    if event_type == 'message':
        return handle_message(event)
    else:
        return ""

def handle_message(event):
    # 處理訊息事件
    user_message = event['message']['text'].strip()
    user_message_type = event['message']['type']
    user_id = event['source']['userId']
    group_id = event['source'].get('groupId', '請將Line bot加入群組後於群組輸入gid重新查詢')
    room_id = event['source'].get('roomId', '請將Line bot加入聊天室後於聊天室輸入rid重新查詢')
    keys_list = list(app.config['confirm_list'].keys())
    values_list = list(app.config['confirm_list'].values())    
    
    if user_message_type == 'text':
        if user_message.lower() == "help":
            return f"我是物聯網機器人。\n輸入id：查詢userId\n輸入gid：查詢groupId\n輸入rid：查詢roomId\n輸入led：LED指令選單"        
        elif user_message.lower() == "id":
            return user_id
        elif user_message.lower() == "gid":
            return group_id
        elif user_message.lower() == "rid":
            return room_id
        elif user_message.lower() == "led":
            reply_token = event['replyToken']
            reply_message = [
                {
                    "type": "template",
                    "altText": "this is a confirm template",
                    "template": {
                        "type": "confirm",
                        "actions": [
                            {
                                "type": "message",
                                "label": keys_list[0],
                                "text": values_list[0]
                            },
                            {
                                "type": "message",
                                "label": keys_list[1],
                                "text": values_list[1]
                            }
                        ],
                        "text": "燈光控制"
                    }
                }
            ]              
            reply_message_to_line_bot(CHANNEL_ACCESS_TOKEN, reply_token, reply_message)
            
            return ""
        elif user_message.lower() == values_list[0]:
            return "燈光開啟"
        elif user_message.lower() == values_list[1]:
            return "燈光關閉"		
        else:
            return ""
    else:
        return ""