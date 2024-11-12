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
app.config['Project_title'] = '聯發科造課師(法蘭斯)的SQL查詢資料表'

# 設定Google試算表
app.config['sheetID'] = '1PfmtHNPQvamES8uZwxCbn1A14C5_KWhbj-k02uVXYGM'
app.config['sheetName'] = '花園,溫室'

# 定義一個路由，當接收到 POST 請求時觸發此函數
@app.route('/', methods=['POST'])
def home():
    try:
        # 設定初始值
        sheetname = ''
        sql = ''
		
        # 從 POST 請求中取得 JSON 格式參數資料
        jsonData = request.get_json()
        if jsonData is not None:
            sheetname = str(jsonData.get('sheetname', ''))
            sql = str(jsonData.get('sql', ''))
			
        # 檢查參數值是否有效
        if sheetname not in app.config['sheetName'].split(','):
            raise ValueError(f"Sheet name is missing or invalid. Choices: {app.config['sheetName']}")
        if sql == '' or 'FROM' in sql:
            raise ValueError("SQL is missing or invalid")			
            
        # 對 SQL 查詢進行 URL 編碼
        urlencode_sheetname = urlencode({'sheet': sheetname})		
        urlencode_sql = urlencode({'tq': sql})
        
        # 發送 HTTP 請求以取得Google試算表SQL查詢資料  
        url = f"https://docs.google.com/spreadsheets/d/{app.config['sheetID']}/gviz/tq?tqx=out:json&{urlencode_sheetname}&{urlencode_sql}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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


'''
# Vercel環境下不用加入以下程式碼

if __name__ == '__main__':
    app.run(debug=True)
'''
