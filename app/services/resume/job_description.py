from typing import List
from pydantic import BaseModel, ValidationError
from app.schemas.resume import JobAnalysis, AiAnalysisResponse
from app.chain.job_description import chain

class JobAnalysis(BaseModel):
    company: str
    position: str
    mainTasks: List[str]
    requirements: List[str]
    career: str
    resumeRequirements: List[str]
    recruitmentProcess: List[str]

class AiAnalysisResponse(BaseModel):
    analysis: JobAnalysis

async def analyze_job_description(raw_data: str) -> AiAnalysisResponse:
    """채용공고 분석"""
    try:
        # LangChain을 사용하여 분석 수행
        result = await chain.ainvoke({"text": raw_data})
        
        print("\n=== AI 분석 원본 결과 ===")
        print(result)
        print("=======================\n")
        
        return result
        
    except Exception as e:
        print(f"채용공고 분석 중 오류 발생: {str(e)}")
        # 기본 응답 반환
        default_analysis = JobAnalysis(
            company="회사명을 찾을 수 없습니다.",
            position="직무를 찾을 수 없습니다.",
            mainTasks=["주요 업무를 찾을 수 없습니다."],
            requirements=["자격 요건을 찾을 수 없습니다."],
            career="경력 요구사항을 찾을 수 없습니다.",
            resumeRequirements=["이력서", "자기소개서"],
            recruitmentProcess=["서류 전형", "1차 면접", "2차 면접", "최종 면접"]
        )
        return AiAnalysisResponse(analysis=default_analysis)

