# 匯入 Flask 模組及其函數，用於建立 Web 應用程式和處理 JSON 請求
from flask import Flask, jsonify, request
# 匯入 urllib 模組中的 urlopen 和 Request，用於發送 HTTP 請求    
from urllib.request import urlopen, Request
# 匯入 urllib 模組中的 urlencode，用於編碼 URL 查詢參數
from urllib.parse import urlencode
# 匯入 JSON 模組，用於處理 JSON 資料 
import json 

"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3
"""

# 建立 Flask 應用程式實例
app = Flask(__name__)                     

# 設定專案標題
app.config['Project_title'] = '聯發科造課師(法蘭斯)的驗證密碼智慧燈'
app.config['Project_password'] = '12345678'
app.config['variable_val'] = ['1', '0']

# 定義一個路由，當接收到 POST 請求時觸發此函數
@app.route('/', methods=['POST'])
def home():
    try:
        # 設定初始值
        password = ''		
        val = ''
		
        # 從 POST 請求中取得 JSON 格式參數資料
        jsonData = request.get_json()
        if jsonData is not None:
            password = str(jsonData.get('password', ''))		
            val = str(jsonData.get('val', ''))

        if password != app.config['Project_password']:
            raise ValueError("Password is invalid. Please provide the password for authentication.")
			
        # 檢查參數資料是否正確
        if val not in app.config['variable_val']:
            raise ValueError("The URL parameter val is invalid. Please state whether to turn the light on or off in the conversation.")			
			
        # 根據獲取的狀態設定對應的中文狀態描述
        status_message = "Led ON" if val == '1' else "Led OFF" if val == '0' else "Nothing"    
		
        # 構建回應資料並返回
        response_data = {
            "data": status_message
        }
        return jsonify(response_data), 200

    except Exception as e:
	
        # 構建執行錯誤資訊並返回	
        response_data = {
            "data": f"An error occurred: {e}"
        }	    
        return jsonify(response_data), 500

# 定義一個路由 /ablout觸發此函數
@app.route('/about')
def about():
    return app.config['Project_title']