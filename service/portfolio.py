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
llm = ChatOpenAI(
    temperature=0.3, 
    model_name="gpt-4o",  # 더 큰 컨텍스트를 지원하는 모델로 변경
    max_tokens=4096,  # 출력 토큰 수 제한
    request_timeout=300  # 타임아웃 시간 증가
)

# 체인 구성
chain = prompt | llm | parser

async def generate_portfolio(user_id: str, repositories: list) -> Union[PortfolioData, Dict[str, Any]]:
    start_time = time.time()
    
    try:
        if not repositories:
            print(f"사용자 {user_id}의 저장소 정보가 없습니다.")
            return {"error": "분석할 저장소가 없습니다."}
            
        code_contents = []
        for repo_path in repositories:
            try:
                # 전체 저장소 경로 구성
                full_repo_path = Path("repository/data") / repo_path
                print(f"저장소 경로: {full_repo_path}")
                
                # 저장소 내의 모든 파일 검색
                for file_path in full_repo_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in [
                        '.py', '.java', '.js', '.html', '.css', '.ts', '.jsx', '.tsx'
                    ]:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                # 파일이 너무 크면 일부만 사용
                                if len(content) > 5000:
                                    content = content[:5000] + "\n... (내용 생략) ..."
                                
                                code_contents.append({
                                    "file": str(file_path.relative_to(full_repo_path)),
                                    "content": content
                                })
                                print(f"파일 처리됨: {file_path.name}")
                        except Exception as e:
                            print(f"파일 읽기 오류 {file_path}: {str(e)}")
            except Exception as e:
                print(f"저장소 처리 오류 {repo_path}: {str(e)}")
        
        if not code_contents:
            return {"error": "처리 가능한 소스 코드 파일이 없습니다."}

        # 소스 코드 텍스트 생성
        source_code_text = "\n\n".join([
            f"=== {file['file']} ===\n{file['content']}" 
            for file in code_contents
        ])
        
        # LangChain 체인으로 포트폴리오 생성
        try:
            response = chain.invoke({"source_code": source_code_text})
            processing_time = time.time() - start_time
            print(f"포트폴리오 생성 시간: {processing_time:.2f}초")
            return response
        except Exception as chain_error:
            print(f"포트폴리오 생성 중 파싱 오류: {str(chain_error)}")
            raw_response = llm.invoke(prompt.format(source_code=source_code_text))
            print(f"원본 응답: {raw_response}")
            return {
                "error": "포트폴리오 형식 파싱 실패",
                "raw_response": raw_response.content
            }
        
    except Exception as e:
        print(f"포트폴리오 생성 중 오류: {str(e)}")
        return {
            "error": f"포트폴리오 생성 실패: {str(e)}",
            "processing_time": time.time() - start_time
        }