import os
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import datetime
import json # JSON 파싱을 위해 추가

load_dotenv()

if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class CareerAI:
    def __init__(self):
        if not os.getenv("GOOGLE_API_KEY"):
            return
        
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="career_collection", 
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def load_data(self, data_list):
        if not os.getenv("GOOGLE_API_KEY"): return
        if self.collection.count() > 0: return 
        
        ids = [str(i) for i in range(len(data_list))]
        documents = [item['content'] for item in data_list]
        metadatas = [{"source": item['source'], "category": item['category']} for item in data_list]

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print("✅ 초기 데이터 로드 완료")

    def add_new_tip(self, category, source, content):
        if not os.getenv("GOOGLE_API_KEY"): return False
        new_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            self.collection.add(
                documents=[content],
                metadatas=[{"category": category, "source": source}],
                ids=[new_id]
            )
            return True
        except Exception as e:
            print(f"학습 실패: {e}")
            return False

    def get_coaching(self, user_text):
        """자소서 내용을 분석하고 첨삭해주는 함수"""
        if not os.getenv("GOOGLE_API_KEY"):
            return "API 키가 없습니다.", [], None

        # RAG 검색
        results = self.collection.query(query_texts=[user_text], n_results=3)
        
        found_tips = ""
        sources = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                source_info = f"{meta['category']} - {meta['source']}"
                found_tips += f"- {source_info}: {doc}\n"
                sources.append(source_info)

        # 1차 분석 (문제점 발굴)
        draft_prompt = f"""
        당신은 꼼꼼한 '이력서 교정 에디터'입니다.
        [참고 가이드]를 기준으로 [사용자 글]을 분석하여, 수정이 시급한 문장 3~5개를 찾아내세요.
        전체적인 내용을 요약하지 말고, 구체적인 '문장 단위'의 문제점을 지적해야 합니다.

        [참고 가이드]
        {found_tips}

        [사용자 글]
        {user_text}
        """
        
        try:
            draft_response = self.model.generate_content(draft_prompt)
            draft_text = draft_response.text
        except Exception as e:
            return f"분석 중 에러: {str(e)}", [], None

        # 2차 코칭 (쪽집게 과외 스타일)
        refine_prompt = f"""
        당신은 합격률 99%의 취업 컨설턴트입니다.
        앞선 [분석 내용]을 바탕으로, 의뢰인에게 **구체적인 수정 제안(첨삭)**을 해주세요.
        
        반드시 아래 **[출력 형식]**을 지켜서 답변하세요.

        [분석 내용]
        {draft_text}

        [사용자 원문]
        {user_text}

        [출력 형식]
        **총평:** (전체적인 느낌과 주요 개선 방향 1~2줄 요약)
        ---
        **1. 🔴 원문:** "(문제가 되는 사용자의 문장을 그대로 인용)"
           **💡 이유:** (왜 이 문장이 별로인지 설명)
           **🟢 수정 제안:** "(이렇게 고쳐보세요)"

        **2. 🔴 원문:** ...
           **💡 이유:** ...
           **🟢 수정 제안:** ...
        ---
        **마무리 조언:** (자신감을 주는 멘트)
        """

        try:
            final_response = self.model.generate_content(refine_prompt)
            return final_response.text, sources, draft_text 
        except Exception as e:
            return f"코칭 중 에러: {str(e)}", [], None

    def parse_resume_to_json(self, raw_text):
        """
        통짜 이력서 텍스트를 분석하여 구조화된 JSON으로 반환하는 함수 (신규 추가)
        """
        if not os.getenv("GOOGLE_API_KEY"):
            return {"error": "API Key Missing"}

        parse_prompt = f"""
        당신은 '이력서 데이터 추출기'입니다.
        아래 [입력 텍스트]를 분석하여 경력 사항을 구조화된 JSON 포맷으로 변환하세요.
        
        [규칙]
        1. 불필요한 서술어는 제거하고 핵심만 추출하세요.
        2. 날짜/기간이 명확하지 않으면 "Unknown"으로 표시하세요.
        3. **오직 JSON 데이터만 출력하세요.** (마크다운 ```json 태그 포함 금지)
        
        [추출할 필드 구조]
        {{
            "summary": "전체 경력 1줄 요약",
            "experiences": [
                {{
                    "company": "회사명",
                    "role": "직무/역할",
                    "period": "근무 기간",
                    "details": ["성과 1", "성과 2", "성과 3"]
                }}
            ]
        }}

        [입력 텍스트]
        {raw_text}
        """

        try:
            response = self.model.generate_content(parse_prompt)
            result_text = response.text.strip()

            # JSON 파싱 (AI가 가끔 ```json ... ``` 을 붙일 때가 있어서 제거 처리)
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "")
            
            return json.loads(result_text)

        except Exception as e:
            return {"error": f"파싱 실패: {str(e)}", "raw_response": result_text}