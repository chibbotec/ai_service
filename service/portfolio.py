import os
import time
import glob
from pathlib import Path
from typing import Dict, Any, Union
from schemas import PortfolioData, SystemArchitecture
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

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
4. 주요 기능은 도메인별로 그룹화하여 작성하고, 각 기능에 대한 자세한 설명을 포함해주세요.
   예시 형식: {{"기능명": ["설명1", "설명2", ...]}}
5. 시스템 아키텍처는 다음 구성요소를 포함해 주세요:
   - overview: 전체 아키텍처 개요
   - components: 각 서비스 구성요소와 포트, 설명, 주요 기능
   - tech_stack: 기술 스택을 카테고리별로 분류
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
llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o")

# 체인 구성
chain = prompt | llm | parser

async def generate_portfolio(user_id: str) -> Union[PortfolioData, Dict[str, Any]]:
    """
    사용자 소스코드를 기반으로 포트폴리오 내용을 생성합니다.
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        포트폴리오 데이터 또는 에러 정보를 담은 딕셔너리
    """
    start_time = time.time()
    
    try:
        # 사용자 소스 코드 디렉토리 경로
        source_dir = Path(f"./data/src/{user_id}")
        
        # 디렉토리가 존재하지 않으면 에러 반환
        if not source_dir.exists():
            print(f"사용자 {user_id}의 소스 디렉토리가 없습니다.")
            return {"error": "소스 코드를 찾을 수 없습니다."}
            
        # 소스 코드 파일 읽기
        source_files = []
        # for ext in ['*.java', '*.py', '*.js', '*.html', '*.css', '*.ts', '*.jsx', '*.tsx']:
        for ext in ['*.*']:    
            source_files.extend(glob.glob(str(source_dir / "**" / ext), recursive=True))
        
        # 파일 내용 수집
        code_contents = []
        for file_path in source_files:
            rel_path = os.path.relpath(file_path, start=str(source_dir))
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # 파일이 너무 크면 일부만 사용
                    if len(content) > 5000:
                        content = content[:5000] + "\n... (내용 생략) ..."
                    
                    code_contents.append({
                        "file": rel_path,
                        "content": content
                    })
            except Exception as e:
                print(f"파일 읽기 오류 {file_path}: {str(e)}")
        
        # 소스 코드 텍스트 생성
        source_code_text = "\n\n".join([f"=== {file['file']} ===\n{file['content']}" for file in code_contents])
        
        # LangChain 체인으로 포트폴리오 생성
        try:
            response = chain.invoke({"source_code": source_code_text})
            processing_time = time.time() - start_time
            print(f"포트폴리오 생성 시간: {processing_time:.2f}초")
            return response
        except Exception as chain_error:
            print(f"포트폴리오 생성 중 파싱 오류: {str(chain_error)}")
            # 응답을 받았지만 파싱에 실패한 경우, JSON 형식으로 수동 변환 시도
            raw_response = llm.invoke(prompt.format(source_code=source_code_text))
            print(f"원본 응답: {raw_response}")
            return {
                "error": "포트폴리오 형식 파싱 실패",
                "raw_response": raw_response.content
            }
        
    except Exception as e:
        print(f"포트폴리오 생성 중 오류: {str(e)}")
        # 오류 발생 시 자세한 정보 반환
        return {
            "error": f"포트폴리오 생성 실패: {str(e)}",
            "processing_time": time.time() - start_time
        }