from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.resume import PortfolioRequest, ResumeSummaryRequest, ResumeSummary, JobDescriptionRequest, CustomResumeRequest
from app.services.resume import generate_portfolio, get_portfolio_status, generate_resume_summary
from app.services.resume.job_description import analyze_job_description
from app.crawler.main_crawler import crawl_url
from app.services.resume.custom_resume import generate_custom_resume, get_custom_resume_status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["resume"]
)

@router.post("/{space_id}/resume/{user_id}/create-portfolio")
async def create_portfolio(space_id: str, user_id: str, request: PortfolioRequest, background_tasks: BackgroundTasks):
    try:
        print(f"포트폴리오 생성 요청: 사용자 ID={user_id}")
        
        # 백그라운드 작업으로 포트폴리오 생성 시작
        background_tasks.add_task(generate_portfolio, user_id, request.repositories, request.commitFiles)
        
        # 즉시 응답 반환
        return JSONResponse(
            status_code=202,
            content={
                "message": "포트폴리오 생성이 시작되었습니다.",
                "status": "processing",
                "user_id": user_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 생성 요청 처리 오류: {str(e)}")

@router.get("/{space_id}/resume/{user_id}/portfolio-status")
async def check_portfolio_status(space_id: str, user_id: str):
    status = await get_portfolio_status(user_id)
    if "error" in status:
        if status["error"] == "포트폴리오 생성 요청을 찾을 수 없습니다.":
            raise HTTPException(status_code=404, detail=status["error"])
        raise HTTPException(status_code=500, detail=status["error"])
    return status

@router.post("/{space_id}/resume/{user_id}/summary", response_model=ResumeSummary)
async def create_resume_summary(space_id: str, user_id: str, request: ResumeSummaryRequest):
    try:
        print(f"이력서 요약 생성 요청: 사용자 ID={user_id}")
        
        # 이력서 요약 생성
        result = await generate_resume_summary(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 요약 생성 처리 오류: {str(e)}")

@router.post("/{space_id}/resume/job-description")
async def create_job_description(space_id: str, request: JobDescriptionRequest):
    try:
        print(f"채용공고 크롤링 요청: URL={request.url}")
        
        # 크롤러 호출
        result = crawl_url(request.url)
        
        if not result:
            raise HTTPException(status_code=400, detail="URL 크롤링에 실패했습니다.")
            
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        # 채용공고 분석
        analysis_result = await analyze_job_description(result['raw_data'])
        
        return {
            "status": "success",
            "site": result['site'],
            "url": result['url'],
            "analysis": analysis_result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 크롤링 처리 오류: {str(e)}")
    
@router.post("/{space_id}/resume/{user_id}/custom-resume")
async def create_custom_resume(space_id: str, user_id: str, request: CustomResumeRequest):
    try:
        logger.info(f"커스텀 이력서 생성 요청: 사용자 ID={user_id}, 타입={request.type}")
        
        # 요청 데이터 검증
        if not request.jobDescription:
            raise HTTPException(status_code=400, detail="채용 공고 정보가 필요합니다.")
        
        if request.type == "resume" and not request.selectedResume:
            raise HTTPException(status_code=400, detail="이력서 정보가 필요합니다.")
        
        if request.type == "portfolio" and not request.selectedPortfolio:
            raise HTTPException(status_code=400, detail="포트폴리오 정보가 필요합니다.")
        
        # 커스텀 이력서 생성
        result = await generate_custom_resume(user_id, request)
        
        # 에러가 있는 경우 HTTP 예외로 변환
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"커스텀 이력서 생성 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"커스텀 이력서 생성 처리 오류: {str(e)}")
    
@router.get("/{space_id}/resume/{user_id}/custom-resume-status")
async def check_custom_resume_status(space_id: str, user_id: str):
    try:
        status = await get_custom_resume_status(user_id)
        if "error" in status:
            if status["error"] == "커스텀 이력서 생성 요청을 찾을 수 없습니다.":
                raise HTTPException(status_code=404, detail=status["error"])
            raise HTTPException(status_code=500, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"커스텀 이력서 상태 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"커스텀 이력서 상태 조회 오류: {str(e)}")