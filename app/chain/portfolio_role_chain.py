from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume import PortfolioRole

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=PortfolioRole)

# 프롬프트 템플릿 생성
template = """
당신은 IT채용 전문가입니다. 주어진 소스 코드와 커밋 정보를 분석하여 개발자의 주요 역할과 기여도를 파악해 주세요.

{format_instructions}

다음 정보를 기반으로 개발자의 역할과 기여도를 분석해 주세요:

소스 코드:
{source_code}

커밋 정보:
{commit_files}

다음 지침을 따라 역할과 기여도를 분석해 주세요:

1. 주요 역할 및 성과:
   - 각 항목은 반드시 "{{기술}}을 사용해서 {{기능}} 구현 {{성과}}" 형식으로 작성해 주세요.
   - 성과는 구체적인 수치나 개선 효과를 포함해야 합니다.
   - 예시: "Terraform을 사용해서 클라우드 인프라 프로비저닝 자동화하여 배포 시간 80% 단축"
   - 예시: "GitAction을 사용해서 무중단 배포 파이프라인 구축하여 서비스 다운타임 제로 달성"
   - 예시: "API Gateway를 사용해서 서비스 간 연결 아키텍처 설계하여 API 평균 응답시간 58ms 단축"
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["source_code", "commit_files"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-4.1-nano",
    max_tokens=32768,
    request_timeout=500
)

# 체인 구성
role_chain = prompt | llm | parser
