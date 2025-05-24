from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume import ResumeSummary

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=ResumeSummary)

# 프롬프트 템플릿 생성
template = """
당신은 IT 채용 전문가입니다. 주어진 이력서 정보를 분석하여 기술 스택 요약을 생성해 주세요.

{format_instructions}

다음 이력서 정보를 기반으로 기술 스택 요약을 작성해 주세요:

지원 포지션: {position}

프로젝트 정보:
{projects}

경력 정보:
{careers}

다음 지침을 따라 기술 스택 요약을 작성해 주세요:
1. 지원자의 프로젝트와 경력을 분석하여 가장 적합한 기술 스택을 추천해 주세요.
2. 각 기술 스택에 대한 구체적인 성과와 경험을 포함해 주세요.
3. 기술 스택은 실제 사용된 기술과 추천 기술을 모두 포함해 주세요.
4. 각 기술 스택에 대한 설명은 구체적인 수치와 성과를 포함해 주세요.

프로젝트 정보는 다음 형식으로 제공됩니다:
- name: 프로젝트 이름
- techStack: 사용된 기술 스택 목록
- role: 프로젝트에서의 역할과 성과

경력 정보는 다음 형식으로 제공됩니다:
- position: 직무
- achievement: 주요 성과

빈 값이 있는 경우 해당 정보는 무시하고 분석해 주세요.
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["position", "projects", "careers"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-4.1",
    max_tokens=32768,
    request_timeout=300
)

# 체인 구성
chain = prompt | llm | parser
