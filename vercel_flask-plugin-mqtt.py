"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3
Flask-MQTT==1.2.1
"""

# 匯入 Flask 模組及其函數，用於建立 Web 應用程式和處理 JSON 請求
from flask import Flask, jsonify, request
# 匯入 Flask-MQTT 模組，用於 MQTT 通訊
from flask_mqtt import Mqtt
# 匯入 urllib 模組中的 urlopen 和 Request，用於發送 HTTP 請求    
from urllib.request import urlopen, Request
# 匯入 urllib 模組中的 urlencode，用於編碼 URL 查詢參數
from urllib.parse import urlencode
# 匯入 JSON 模組，用於處理 JSON 資料 
import json
# 匯入 time 模組，用於延遲
import time

# 建立 Flask 應用程式實例
app = Flask(__name__)

# 設定 MQTT 相關設定
app.config['MQTT_BROKER_URL'] = 'broker.MQTTGO.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_PUBLISH_TOPIC'] = 'test/plugin/publish'
app.config['MQTT_SUBSCRIBE_TOPIC'] = 'test/plugin/subscribe'

# 設定MQTT接收的訊息
app.config['MQTT_SUBSCRIBE_MESSAGE'] = ''

# 初始化 Flask-MQTT       
mqtt = Mqtt(app)                   

# 設定專案標題
app.config['Project_title'] = '聯發科造課師(法蘭斯)的智慧燈'

# 限定參數的值
app.config['variable_val'] = ['1', '0']

# 定義一個路由，當接收到 POST 請求時觸發此函數
@app.route('/', methods=['POST'])
def home():
    try:
        # 設定初始值
        val = ''       
        app.config['MQTT_SUBSCRIBE_MESSAGE'] = ''
        
        # 從 POST 請求中取得 JSON 格式參數資料
        jsonData = request.get_json()
        if jsonData is not None:
            val = str(jsonData.get('val', ''))
        
        # 檢查參數資料是否正確
        if val not in app.config['variable_val']:
            raise ValueError("The URL parameter val is invalid. Please state whether to turn the light on or off in the conversation.")       
    
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
            raise ValueError(f"Failed to send MQTT message '{val}'. Error code: {result}")
        else:
            i = 0
            while app.config['MQTT_SUBSCRIBE_MESSAGE'] == '' and i < 5:  # 等待5秒內物聯網設備回傳MQTT訊息
                time.sleep(1)  # 間隔1秒
                i += 1

        # 如果無法取得IoT設備的MQTT回傳訊息
        if app.config['MQTT_SUBSCRIBE_MESSAGE'] == '':
            app.config['MQTT_SUBSCRIBE_MESSAGE'] = 'Unable to obtain device control status'
            
        # 構建回應資料並返回
        response_data = {
            "data": {
                "python": 'OK', 
                "device": app.config['MQTT_SUBSCRIBE_MESSAGE']
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
    
        # 構建執行錯誤資訊並返回    
        response_data = {
            "data": {
                "error": f"An error occurred: {e}"
            }            
        }    
        return jsonify(response_data), 500

# 定義一個路由 /about 觸發此函數
@app.route('/about')
def about():
    return app.config['Project_title']

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


'''
# Vercel環境下不用加入以下程式碼

if __name__ == '__main__':
    app.run(debug=True)
'''
