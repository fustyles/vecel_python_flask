"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3

Python online
https://www.onlinegdb.com/
GeminiKey加解密
https://github.com/fustyles/vecel_python_flask/edit/main/vercel_flask-linebot-geminiKey_encrypt.py
"""

# 引入 Flask 框架及其相關模組
from flask import Flask, jsonify, request  
# 引入 http.client 模組，用於發送 HTTP 請求
import http.client  
# 引入 json 模組，用於處理 JSON 資料
import json
# 匯入 re 模組，用於正則表達式操作
import re

app = Flask(__name__)

# 設定專案標題
app.config['Project_title'] = '法蘭斯的ChatBot'

# Line Bot CHANNEL ACCESS TOKEN
CHANNEL_ACCESS_TOKEN = "iSHcOEyq3PM0Oe/PvgmCY69jAOdW6cWoj1Zn34VFgduEJzGlWWcZnAo6LjMt3L9EAldBB4erN2yt/E5tXQNQt7jSyOGKseY2jPD8czzI/RURL7jF/PBKtGm8PwIIymzXcqqdZLP2zaKRhliJUIMdJQdB04t89/1O/w1cDnyilFU=123"

# Gemini Key (Encrypted)
GeminiKey = "DLcdVbFKegN3kbGnUidgBBMCaxg7MqC7deOwDP8123"
# Gemini Key Decrypt Shift
GeminiKeyShift = 3

# Gemini Assistant Behavior
geminiBehavior = "請分析對話中的情境決定是否開關電燈。\n(1)若判斷情境可能需要開電燈回傳1、可能需要關電燈回傳0，無法判斷或無關或表達模糊回傳-1。\n(2)回傳內容只能是1、0、-1其中之一。\n(3)請不要多做解釋！\n\n\n\n"

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
            return f"我是Gemini聊天機器人。\n\n輸入id：查詢userId\n輸入gid：查詢groupId\n輸入rid：查詢roomId\n\n助手行為：\n{geminiBehavior}"        
        elif user_message.lower() == "id":
            return user_id
        elif user_message.lower() == "gid":
            return group_id
        elif user_message.lower() == "rid":
            return room_id            
        else:
            return handle_gemini(user_message, caesar_decrypt(GeminiKey, GeminiKeyShift))
    else:
        return ""

def handle_gemini(message, key):
    try:
        # 設定請求的 URL
        url = f"/v1beta/models/gemini-1.5-flash-latest:generateContent?key={key}"
        host = "generativelanguage.googleapis.com"

        # 構建請求的資料
        payload = {
            "contents": [
                {
                    "parts": [                       
                        {
                            "text": f"{geminiBehavior}\n{message}"
                        }
                    ]
                }
            ]
        }

        # 設定 HTTP 請求
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        # 建立 HTTP 連接
        conn = http.client.HTTPSConnection(host)
        conn.request("POST", url, body=json.dumps(payload), headers=headers)

        # 獲取 HTTP 回應
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()

        # 解析 JSON 回應
        json_response = json.loads(response_data)
        response_text = json_response["candidates"][0]["content"]["parts"][0]["text"]
        if response_text == "null":
            response_text = json_response["error"]["message"]

        return re.sub(r'[\n\r\t]', '', response_text).strip()
        
    except Exception as e:
        return str(e)

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
