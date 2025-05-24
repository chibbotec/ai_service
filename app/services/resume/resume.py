from app.chain.resume_summary_chain import chain
from app.schemas.resume import ResumeSummaryRequest, ResumeSummary

async def generate_resume_summary(request: ResumeSummaryRequest) -> ResumeSummary:
    """
    이력서 요약을 생성하는 함수
    
    Args:
        request (ResumeSummaryRequest): 이력서 요약 요청 데이터
        
    Returns:
        ResumeSummaryResponse: 생성된 이력서 요약
    """
    try:
        # 체인 실행
        result = await chain.ainvoke({
            "position": request.position,
            "projects": request.projects,
            "careers": request.careers
        })
        
        return result
    except Exception as e:
        raise Exception(f"이력서 요약 생성 중 오류 발생: {str(e)}")
