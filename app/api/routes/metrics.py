from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(
    prefix="/api/v1",
    tags=["metrics"]
)

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)