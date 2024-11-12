"""
Author : ChungYi Fu (Kaohsiung, Taiwan)   2024/11/11 22:00
https://www.facebook.com/francefu

設定requirements.txt
Flask==3.0.3
"""

# 匯入 Flask 模組及其函數，用於建立 Web 應用程式和處理 JSON 請求
from flask import Flask, jsonify, request
# 匯入 urllib 模組中的 urlopen 和 Request，用於發送 HTTP 請求    
from urllib.request import urlopen, Request
# 匯入 urllib 模組中的 urlencode，用於編碼 URL 查詢參數
from urllib.parse import urlencode
# 匯入 JSON 模組，用於處理 JSON 資料 
import json 

# 建立 Flask 應用程式實例
app = Flask(__name__)                      

# 設定專案標題
app.config['Project_title'] = '聯發科造課師(法蘭斯)的網站資料'

# 定義一個路由，當接收到 POST 請求時觸發此函數
@app.route('/', methods=['POST'])
def home():
    try:
        # 設定初始值
        val = ''
		
        # 從 POST 請求中取得 JSON 格式參數資料
        jsonData = request.get_json()
        if jsonData is not None:
            val = str(jsonData.get('val', ''))
        
        # 檢查 val 是否有效
        if val == '':
            raise ValueError("URL is missing or invalid")    
        
        # 發送 HTTP 請求以取得網站的網頁資料
        req = Request(val, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response:
            remoteData = response.read().decode('utf-8')
		
        # 構建回應資料並返回
        response_data = {
            "data": remoteData
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