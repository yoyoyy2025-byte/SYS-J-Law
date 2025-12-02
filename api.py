from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_system import CareerAI
from career_data import CAREER_TIPS
from user_db import init_user_db, save_message

# 1. 앱 초기화
app = FastAPI(title="Job-Navigator API", description="AI 자소서 코칭 백엔드 서버")

# 2. CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://project-sys-j.onrender.com", # 배포된 주소도 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. AI 시스템 로드
print("🚀 AI 시스템 로딩 중...")
ai_system = CareerAI()
ai_system.load_data(CAREER_TIPS)
init_user_db()
print("✅ 로딩 완료!")

# ------------------------------------------------------------------
# 4. 데이터 모델 정의 (주문서 양식)
# ------------------------------------------------------------------
class CoachingRequest(BaseModel):
    user_input: str  # 자소서 내용 (코칭용)

class ParseRequest(BaseModel):
    raw_resume: str  # 통짜 이력서 텍스트 (파싱용) - 🔥 신규 추가

# ------------------------------------------------------------------
# 5. API 엔드포인트 (메뉴판)
# ------------------------------------------------------------------

# [메뉴 1] 자소서 코칭 (기존 기능)
@app.post("/api/coach")
async def get_coaching(request: CoachingRequest):
    try:
        response_text, sources, draft_text = ai_system.get_coaching(request.user_input)
        save_message(request.user_input, response_text)
        return {
            "status": "success",
            "answer": response_text,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [메뉴 2] 이력서 JSON 변환 (🔥 신규 추가된 기능!)
# 외부에서 'POST /api/parse' 주소로 요청하면 이 함수가 실행됩니다.
@app.post("/api/parse")
async def parse_resume(request: ParseRequest):
    try:
        # 주방장(rag_system)에게 파싱 시키기
        parsed_data = ai_system.parse_resume_to_json(request.raw_resume)
        
        return {
            "status": "success",
            "data": parsed_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. 헬스 체크
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Job-Navigator API is running"}