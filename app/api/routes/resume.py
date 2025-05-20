from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.resume import PortfolioRequest
from app.services.resume import generate_portfolio, get_portfolio_status
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["resume"]
)

@router.post("/{space_id}/resume/{user_id}/create-portfolio")
async def create_portfolio(space_id: str, user_id: str, request: PortfolioRequest, background_tasks: BackgroundTasks):
    try:
        print(f"포트폴리오 생성 요청: 사용자 ID={user_id}")
        
        # 백그라운드 작업으로 포트폴리오 생성 시작
        background_tasks.add_task(generate_portfolio, user_id, request.repositories)
        
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
