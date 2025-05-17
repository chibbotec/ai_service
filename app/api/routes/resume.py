from fastapi import APIRouter, HTTPException
from app.schemas.resume import PortfolioRequest
from app.services.resume.portfolio import generate_portfolio

router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["resume"]
)

@router.post("/{space_id}/resume/{user_id}/create-portfolio")
async def create_portfolio(space_id: str, user_id: str, request: PortfolioRequest):
    try:
        print(f"포트폴리오 생성 요청: 사용자 ID={user_id}")
    
        # 포트폴리오 생성 서비스 함수 호출
        portfolio_data = await generate_portfolio(user_id, request.repositories)
        
        return portfolio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 답변 생성 오류: {str(e)}")
