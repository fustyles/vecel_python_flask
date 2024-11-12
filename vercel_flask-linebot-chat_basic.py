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
                #回傳request資料 reply_message_to_line_bot(CHANNEL_ACCESS_TOKEN, reply_token, str(msg))
                
                for event in msg['events']:
                    reply_token = event['replyToken']
                    linebot_response = handle_event(event)
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
    elif event_type == 'follow':
        return handle_follow(event)
    elif event_type == 'unfollow':
        return handle_unfollow(event)
    elif event_type == 'join':
        return handle_join(event)
    elif event_type == 'leave':
        return handle_leave(event)
    elif event_type == 'postback':
        return handle_postback(event)
    elif event_type == 'beacon':
        return handle_beacon(event)
    elif event_type == 'accountLink':
        return handle_account_link(event)
    elif event_type == 'memberJoined':
        return handle_member_joined(event)
    elif event_type == 'memberLeft':
        return handle_member_left(event)
    elif event_type == 'things':
        return handle_things(event)
    else:
        return f"Unknown event type: {event_type}"

def handle_message(event):
    # 處理訊息事件
    user_message = event['message']['text'].strip()
    user_message_type = event['message']['type']
    user_id = event['source']['userId']
    group_id = event['source'].get('groupId', '請將Line bot加入群組後於群組輸入gid重新查詢')
    room_id = event['source'].get('roomId', '請將Line bot加入聊天室後於聊天室輸入rid重新查詢')
    
    if user_message_type == 'text':
        if user_message == "id":
            return user_id
        elif user_message == "gid":
            return group_id
        elif user_message == "rid":
            return room_id            
        else:
            return ""
    elif user_message_type == 'image':
        return ""
    elif user_message_type == 'video':
        return ""
    elif user_message_type == 'audio':
        return ""
    elif user_message_type == 'location':
        return ""
    elif user_message_type == 'sticker':
        return ""
    else:
        return ""

def handle_follow(event):
    # 處理追蹤事件
    return "感謝您的追蹤！"

def handle_unfollow(event):
    # 處理取消追蹤事件
    return "很遺憾看到您離開。"

def handle_join(event):
    # 處理加入群組或聊天室事件
    group_id = event['source'].get('groupId', '')    
    return f"{app.config['Project_title']}，大家好！\ngroupId: {group_id}"

def handle_leave(event):
    # 處理離開群組或聊天室事件
    return "再見！"

def handle_postback(event):
    # 處理 postback 事件
    return "您觸發了 postback 事件。"

def handle_beacon(event):
    # 處理 beacon 事件
    return "您進入了 Beacon 範圍。"

def handle_account_link(event):
    # 處理帳號連結事件
    return "帳號連結成功。"

def handle_member_joined(event):
    # 處理成員加入事件
    return "新成員加入了群組。"

def handle_member_left(event):
    # 處理成員離開事件
    return "成員離開了群組。"

def handle_things(event):
    # 處理 LINE Things 事件
    return "收到 LINE Things 裝置的訊息。"


'''
# Vercel環境下不用加入以下程式碼

if __name__ == '__main__':
    app.run(debug=True)
'''


'''
Line Bot 訊息格式
{
  "destination": "xxxxxxxxxx",
  "events": [
    {
      "type": "message",
      "message": {
        "type": "text",
        "id": "14353798921116",
        "text": "Hello, world"
      },
      "timestamp": 1625665242211,
      "source": {
        "type": "user",
        "userId": "U80696558e1aa831..."
      },
      "replyToken": "757913772c4646b784d4b7ce46d12671",
      "mode": "active",
      "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",
      "deliveryContext": {
        "isRedelivery": false
      }
    },
    {
      "type": "follow",
      "timestamp": 1625665242214,
      "source": {
        "type": "user",
        "userId": "Ufc729a925b3abef..."
      },
      "replyToken": "bb173f4d9cf64aed9d408ab4e36339ad",
      "mode": "active",
      "webhookEventId": "01FZ74ASS536FW97EX38NKCZQK",
      "deliveryContext": {
        "isRedelivery": false
      }
    },
    {
      "type": "unfollow",
      "timestamp": 1625665242215,
      "source": {
        "type": "user",
        "userId": "Ubbd4f124aee5113..."
      },
      "mode": "active",
      "webhookEventId": "01FZ74B5Y0F4TNKA5SCAVKPEDM",
      "deliveryContext": {
        "isRedelivery": false
      }
    }
  ]
}
'''
