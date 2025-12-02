import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

class RealTimeLogger:
    def __init__(self, key_path, sheet_name):
        self.key_path = key_path
        self.sheet_name = sheet_name
        self.worksheet = None
        self.conn = None

        # DB/시트 연결 시도
        self._connect_sqlite()
        if os.path.exists(key_path):
            self._connect_gsheet()
        else:
            print(f"⚠️ 경고: {key_path} 파일을 찾을 수 없어 구글 시트 연동을 건너뜁니다.")

    def _connect_gsheet(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.key_path, scope)
            client = gspread.authorize(creds)
            self.worksheet = client.open(self.sheet_name).sheet1
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")

    def _connect_sqlite(self):
        # 상위 폴더가 없으면 생성
        os.makedirs(os.path.dirname('monitor/service.db'), exist_ok=True)
        self.conn = sqlite3.connect('monitor/service.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        self.conn.commit()

    def log(self, user_id, action, details):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] {user_id} : {action}")

        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO user_logs (timestamp, user_id, action, details) VALUES (?, ?, ?, ?)', 
                           (now, user_id, action, details))
            self.conn.commit()
        except Exception as e:
            print(f"DB Error: {e}")

        if self.worksheet:
            try:
                self.worksheet.append_row([now, user_id, action, details])
            except:
                pass