# app/services.py
import time
from app.schemas.interview import InterviewAnswer
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from app.db.repositories.mysql.tech_interview_repository import TechInterviewRepository
from sqlalchemy.orm import Session

# 환경변수 로드
load_dotenv()

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=InterviewAnswer)

# 프롬프트 템플릿 생성
template = """당신은 IT 기술 면접 전문가입니다. 주어진 기술 면접 질문에 대해 모범 답변을 작성해 주세요.

면접 주제: {topic}
면접 질문: {question}
{format_instructions}

다음 지침을 따라 답변을 작성해 주세요:
1. 답변은 명확하고 구체적이어야 합니다.
2. 개념 설명이 필요한 경우 간결하게 설명한 후 실무 적용 방법도 언급해 주세요.
3. 가능한 경우 코드 예시나 실제 사례를 포함해 주세요.
4. 면접관이 중요하게 생각할 포인트도 함께 제공해 주세요.
5. 관련된 추가 지식이나 개념도 간략히 언급해 주세요.
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["topic", "question"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o")

# 체인 구성
chain = prompt | llm | parser

# 기술 면접 답변 생성 함수
async def generate_interview_answer(topic: str, question: str, question_id: int, db: Session) -> InterviewAnswer:
    """
    기술 면접 질문에 대한 AI 답변 생성 및 저장

    Args:
        topic: 면접 주제 (예: "Database", "Network", "Web Security" 등)
        question: 면접 질문 내용
        question_id: 질문 ID
        db: 데이터베이스 세션

    Returns:
        InterviewAnswer: 구조화된 면접 답변
    """
    start_time = time.time()

    try:
        # LangChain 체인 실행
        response = chain.invoke({"topic": topic, "question": question})
        processing_time = time.time() - start_time

        print(f"AI 답변 생성 시간: {processing_time:.2f}초")
        print(f"AI 답변: {response}")

        # 데이터베이스에 답변 저장
        tech_interview_repo = TechInterviewRepository(db)
        
        # 기존 질문 조회
        existing_interview = tech_interview_repo.get_by_id(question_id)
        if not existing_interview:
            raise ValueError(f"Question with id {question_id} not found")
        
        # 기존 질문 업데이트
        existing_interview.ai_answer = response.model_dump_json()
        existing_interview.key_point = response.tips
        existing_interview.additional_topics = response.related_topics
        
        # 업데이트 저장
        updated_interview = tech_interview_repo.update(existing_interview)
        print(f"Successfully updated interview: {updated_interview.id}")

        return response
    except Exception as e:
        print(f"Error generating interview answer: {str(e)}")
        raise e