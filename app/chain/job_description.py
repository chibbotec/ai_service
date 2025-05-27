from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume import JobAnalysis

# LLM 모델과 파서 초기화
parser = PydanticOutputParser(pydantic_object=JobAnalysis)

template = """
다음은 채용공고의 내용입니다. 주어진 텍스트에서 다음 정보를 추출해주세요:

1. 회사명: 정확한 회사명만 추출 (예: "삼성전자", "네이버", "카카오" 등)
2. 직무/포지션: 정확한 직무명만 추출 (예: "백엔드 개발자", "프론트엔드 개발자" 등)
3. 주요 업무: 구체적인 업무 내용을 리스트 형태로 추출 (예: ["API 설계 및 개발", "데이터베이스 설계 및 최적화"] 등)
4. 자격 요건 및 우대 사항: 구체적인 요건을 리스트 형태로 추출 (예: ["3년 이상의 백엔드 개발 경력", "Spring Framework 경험"] 등)
5. 경력 요구사항: 정확한 경력 요구사항만 추출 (예: "3년 이상", "신입/경력" 등)
6. 이력서 요구사항: 구체적인 요구사항을 리스트 형태로 추출 (예: ["이력서", "자기소개서", "포트폴리오"] 등)
7. 채용 절차: 구체적인 절차를 리스트 형태로 추출 (예: ["서류 전형", "1차 면접", "2차 면접", "최종 면접"] 등)

채용공고 내용:
{text}

{format_instructions}

응답은 반드시 다음 형식의 JSON이어야 합니다:
{{
    "company": "회사명",
    "position": "직무/포지션",
    "mainTasks": ["주요 업무1", "주요 업무2"],
    "requirements": ["자격 요건1", "자격 요건2"],
    "career": "경력 요구사항",
    "resumeRequirements": ["이력서 요구사항1 및 설명", "이력서 요구사항2 및 설명"],
    "recruitmentProcess": ["채용 절차1", "채용 절차2"]
}}

예시 응답:
{{
    "company": "네이버",
    "position": "백엔드 개발자",
    "mainTasks": [
        "대규모 트래픽 처리를 위한 서버 설계 및 개발",
        "API 설계 및 구현",
        "데이터베이스 설계 및 최적화"
    ],
    "requirements": [
        "3년 이상의 백엔드 개발 경력",
        "Java/Spring Framework 경험",
        "대규모 트래픽 처리 경험"
    ],
    "career": "3년 이상",
    "resumeRequirements": [
        "이력서",
        "자기소개서",
        "포트폴리오"
    ],
    "recruitmentProcess": [
        "서류 전형",
        "1차 면접",
        "2차 면접",
        "최종 면접"
    ]
}}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo-preview")
chain = prompt | llm | parser
