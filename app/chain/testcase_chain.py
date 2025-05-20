from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.coding_test import TestCaseAnswer

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=TestCaseAnswer)

# 프롬프트 템플릿 생성
template = """당신은 프로그래밍 문제의 테스트 케이스를 생성하는 전문가입니다.
다음 프로그래밍 문제에 대한 테스트 케이스 10개를 생성해주세요.

### 문제 설명
{problem_description}

### 입력 형식
{input_description}

### 출력 형식
{output_description}

### 예시 솔루션 ({solution_language})
{solution_code}
### 테스트 케이스 유형
{test_case_types}

### 특별 요구사항
{additional_requirements}

### 출력 형식 안내
{format_instructions}

테스트 케이스를 생성할 때 다음 지침을 따라주세요:
1. 기본 케이스, 경계 케이스, 특수 케이스를 포함시켜 주세요.
2. 각 테스트 케이스는 입력(.in)과 출력(.out)으로 구성되어야 합니다.
3. 정확히 10개의 테스트 케이스를 생성해주세요.
4. 프로그램의 정확성을 검증할 수 있는 다양한 입력을 포함해주세요.
5. 테스트 케이스의 이름은 1.in, 1.out, 2.in, 2.out 등의 형식으로 지정해주세요.
6. 반드시 "testcases" 키를 가진 배열 형태로 출력해주세요.
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["problem_description", "input_description", "output_description", 
                    "solution_language", "solution_code", "test_case_types", "additional_requirements"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")

# 체인 구성
chain = prompt | llm | parser
