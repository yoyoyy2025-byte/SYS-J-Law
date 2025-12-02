# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ .env 파일에 API 키가 없습니다.")
else:
    try:
        genai.configure(api_key=api_key)
        print("🔍 내 API 키로 사용 가능한 모델 목록:")
        print("-" * 30)
        
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                available_models.append(m.name)
        
        print("-" * 30)
        if not available_models:
            print("⚠️ 사용 가능한 텍스트 생성 모델이 없습니다. API 키 권한을 확인하세요.")
        else:
            print("위 목록 중 하나를 골라 rag_system.py에 넣으세요.")
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}")