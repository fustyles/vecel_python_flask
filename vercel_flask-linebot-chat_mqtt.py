"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3
Flask-MQTT==1.2.1
"""

# 引入 Flask 框架及其相關模組
from flask import Flask, jsonify, request  
# 引入 http.client 模組，用於發送 HTTP 請求
import http.client  
# 引入 json 模組，用於處理 JSON 資料
import json
# 匯入 Flask-MQTT 模組，用於 MQTT 通訊
from flask_mqtt import Mqtt
# 匯入 time 模組，用於延遲
import time
# 匯入 re 模組，用於正則表達式操作
import re

app = Flask(__name__)

# 設定專案標題
app.config['Project_title'] = '法蘭斯的ChatBot'

# Line Bot CHANNEL ACCESS TOKEN
CHANNEL_ACCESS_TOKEN = "iSHcOEyq3PM0Oe/PvgmCY69jAOdW6cWoj1Zn34VFgduEJzGlWWcZnAo6LjMt3L9EAldBB4erN2yt/E5tXQNQt7jSyOGKseY2jPD8czzI/RURL7jF/PBKtGm8PwIIymzXcqqdZLP2zaKRhliJUIMdJQdB04t89/1O/w1cDnyilFU=123"

# 設定 MQTT 相關設定
app.config['MQTT_BROKER_URL'] = 'broker.MQTTGO.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_PUBLISH_TOPIC'] = 'fustyles/gemini/publish'
app.config['MQTT_SUBSCRIBE_TOPIC'] = 'fustyles/gemini/subscribe'

# 設定MQTT接收的訊息
app.config['MQTT_SUBSCRIBE_MESSAGE'] = ''

# 初始化 Flask-MQTT       
mqtt = Mqtt(app)    

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
    
    if user_message_type == 'text':
        if user_message.lower() == "help":
            return f"我是Gemini聊天機器人。\n輸入id：查詢userId\n輸入gid：查詢groupId\n輸入rid：查詢roomId"        
        elif user_message.lower() == "id":
            return user_id
        elif user_message.lower() == "gid":
            return group_id
        elif user_message.lower() == "rid":
            return room_id            
        else:
            mqtt_res = handle_mqtt_sendMessage(user_message)
            if mqtt_res == "ok":
                    return f"MQTT傳送成功： {user_message}\n{app.config['MQTT_SUBSCRIBE_MESSAGE']}"
            else:
                    return f"MQTT傳送失敗： {user_message}"			
    else:
        return ""

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    # 訂閱指定主題
    mqtt.subscribe(app.config['MQTT_SUBSCRIBE_TOPIC'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    # 處理收到的 MQTT 訊息
    topic = message.topic
    payload = message.payload.decode()
    app.config['MQTT_SUBSCRIBE_MESSAGE'] = payload

def handle_mqtt_sendMessage(val):
    app.config['MQTT_SUBSCRIBE_MESSAGE'] = ''
  
    # 構建 MQTT JSON 格式資料並發佈到指定主題
    result, mid = mqtt.publish(app.config['MQTT_PUBLISH_TOPIC'], val)
    
    # 如果 MQTT 傳送失敗重試
    i = 0
    while result != 0 and i < 5:  # 5秒內嘗試重發MQTT訊息
        time.sleep(1)  # 間隔1秒
        i += 1
        result, mid = mqtt.publish(app.config['MQTT_PUBLISH_TOPIC'], val) 

    # 如果 MQTT 依然傳送失敗
    if result != 0:
        return ""
    else:
        i = 0
        while app.config['MQTT_SUBSCRIBE_MESSAGE'] == '' and i < 5:  # 等待5秒內物聯網設備回傳MQTT訊息
            time.sleep(1)  # 間隔1秒
            i += 1

    # 如果無法取得IoT設備的MQTT回傳訊息
    if app.config['MQTT_SUBSCRIBE_MESSAGE'] == '':
        app.config['MQTT_SUBSCRIBE_MESSAGE'] = '但無法取得物聯網裝置以MQTT回傳狀態'

    return "ok"

# 「凱撒密碼」（Caesar Cipher），它通過將每個字母替換為字母表中固定位置的另一個字母來進行加密和解密。
def caesar_encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            encrypted_text += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_text += char
    return encrypted_text

def caesar_decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('A') if char.isupper() else ord('a')
            decrypted_text += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_text += char
    return decrypted_text

'''
# Vercel環境下不用加入以下程式碼

if __name__ == '__main__':
    app.run(debug=True)
'''
