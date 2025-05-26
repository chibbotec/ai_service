from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume import PortfolioData

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=PortfolioData)

# 프롬프트 템플릿 생성
template = """
당신은 IT채용 전문가입니다. 주어진 소스 코드를 분석하여 이력서에 포함할 포트폴리오 내용을 생성해 주세요.

{format_instructions}

다음 소스 코드를 기반으로 프로젝트 포트폴리오를 작성해 주세요:

{source_code}

다음 지침을 따라 포트폴리오를 작성해 주세요:
1. 프로젝트 요약은 간결하고 명확하게 작성해 주세요 (최대 100단어).
2. 프로젝트 개요에는 목적과 문제 해결 방식을 자세히 설명해 주세요 (최대 300단어).
3. 사용된 기술 스택을 모두 리스트로 나열해 주세요.
   예시: ["Spring Boot", "PostgreSQL", "Kafka", "Meilisearch", "WebSocket", "AWS S3", "Docker"]
4. 주요 기능은 도메인별로 그룹화하여 작성하고, 각 기능에 대한 자세한 설명을 포함해주세요.
   예시 형식: {{"기능명": ["설명1", "설명2", ...]}}
   주의: 각 기능의 설명은 반드시 문자열 리스트 형태여야 합니다.
5. 시스템 아키텍처는 다음 구성요소를 포함해 주세요:
   - overview: 전체 아키텍처 개요
   - components: 각 서비스 구성요소와 포트, 설명, 주요 기능
   - tech_stack: 기술 스택을 카테고리별로 분류 (반드시 포함)
   - communication: 서비스 간 통신 방식
   - deployment: 배포 구성 방식
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["source_code"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(
    temperature=0.3, 
    model_name="gpt-4.1-nano",  # 더 큰 컨텍스트를 지원하는 모델로 변경
    max_tokens=32768,  # 출력 토큰 수 제한
    request_timeout=300  # 타임아웃 시간 증가
)

# 체인 구성
chain = prompt | llm | parser
