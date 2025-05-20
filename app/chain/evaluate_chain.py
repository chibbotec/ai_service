from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.interview import Evaluation

# LLM 모델과 파서 초기화
parser = PydanticOutputParser(pydantic_object=Evaluation)

template = """
다음은 기술 면접 문제와 그에 대한 모범답안, 그리고 응시자의 답변입니다.

문제: {problem}

모범답안: {ai_answer}

응시자의 답변: {participant_answer}

위 답변을 평가하여 다음 형식으로 응답해주세요:
{format_instructions}

평가 기준:
1. 핵심 개념의 이해도 (30점)
2. 설명의 정확성과 명확성 (30점)
3. 전문 용어의 적절한 사용 (20점)
4. 답변의 구조와 논리성 (20점)
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["problem", "ai_answer", "participant_answer"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

llm = ChatOpenAI(temperature=0.2, model_name="gpt-4")
chain = prompt | llm | parser 