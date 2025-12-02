import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# ------------------------------------------------------------------
# 🔑 [필수] 아까 넣으셨던 API 키가 맞는지 확인하세요!
# 예: "AIzaSy..."
os.environ["GOOGLE_API_KEY"] = "AIzaSyBb6SIyCPmLEwOQKb9T8c6O4ks7p3lSgrg"
# ------------------------------------------------------------------

print("✅ Google API Key 설정 완료. Gemini 테스트를 시작합니다...")

# 1. Gemini 모델 초기화
try:
    # 🔥 [수정됨] 아까 성공했던 모델 이름 'gemini-flash-latest'로 변경
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.7
    )
except Exception as e:
    print(f"❌ 모델 초기화 실패: {e}")
    exit()

# 2. 프롬프트 템플릿
template = """
당신은 취업 컨설턴트입니다. 아래 [입력된 경험]을 'STAR 기법'으로 다듬어주세요.

[입력된 경험]: {raw_input}

[다듬어진 문장]:
"""

prompt = PromptTemplate(
    input_variables=["raw_input"],
    template=template
)

# 3. 체인 연결 및 실행
chain = prompt | llm

test_input = "편의점 알바할 때 재고 남는 게 아까워서 유통기한 임박 상품 할인 코너 만들었더니 다 팔렸음."

print(f"\n[Input]: {test_input}")
print("-" * 30)

try:
    response = chain.invoke({"raw_input": test_input})
    print(f"[Output]:\n{response.content}")
    print("-" * 30)
    print("🎉 테스트 성공! Gemini & LangChain 환경이 정상입니다.")
except Exception as e:
    print(f"❌ 테스트 실패. 에러 로그를 확인하세요:\n{e}")