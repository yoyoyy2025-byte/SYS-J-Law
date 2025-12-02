import sqlite3
import pandas as pd
from datetime import datetime
import os  # 폴더 생성을 위해 추가

# DB 파일 경로 설정
DB_FOLDER = "monitor"
DB_NAME = f"{DB_FOLDER}/user_history.db"

def init_user_db():
    """사용자 데이터 저장용 DB 테이블 생성"""
    
    # 🔥 [핵심 수정] 폴더가 없으면 자동으로 생성
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"📂 '{DB_FOLDER}' 폴더를 생성했습니다.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(user_input, ai_response):
    """채팅 내용 저장"""
    # 저장 전에도 폴더 확인 (안전장치)
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO history (timestamp, user_input, ai_response) 
        VALUES (?, ?, ?)
    ''', (now, user_input, ai_response))
    
    conn.commit()
    conn.close()

def get_all_history():
    """저장된 모든 데이터 가져오기"""
    # DB 파일이 아예 없으면 빈 데이터프레임 반환
    if not os.path.exists(DB_NAME):
        return pd.DataFrame(columns=["id", "timestamp", "user_input", "ai_response"])

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    conn.close()
    return df