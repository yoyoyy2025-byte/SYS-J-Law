# file_utils.py (새로 만들기)
from pypdf import PdfReader
from docx import Document
import io

def extract_text_from_file(uploaded_file):
    """업로드된 파일(PDF, DOCX)에서 텍스트만 추출하는 함수"""
    text = ""
    
    try:
        # 1. PDF 파일일 경우
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        # 2. Word(DOCX) 파일일 경우
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        # 3. 텍스트 파일일 경우
        elif uploaded_file.name.endswith('.txt'):
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
            
    except Exception as e:
        return f"파일 읽기 오류: {e}"

    return text.strip()