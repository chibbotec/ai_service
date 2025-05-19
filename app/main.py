# app/main.py
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.mongodb.connection import MongoDBConnection
from app.db.mysql.connection import MySQLConnection

from app.api.routes import (
    metrics_router,
    coding_test_router,
    resume_router,
    interview_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트 핸들러"""
    # 시작 시 실행
    try:
        # MongoDB 연결 확인
        mongo_conn = MongoDBConnection()
        mongo_conn.connect()
        await mongo_conn.check_connection()
        print("MongoDB 데이터베이스 연결 확인 완료")
        
        # MySQL 연결 확인
        mysql_conn = MySQLConnection()
        mysql_conn.check_connection()
        print("MySQL 데이터베이스 연결 확인 완료")
        
        yield
    except Exception as e:
        print(f"데이터베이스 연결 실패: {str(e)}")
        raise e
    finally:
        # 종료 시 실행
        mysql_conn = MySQLConnection()
        mysql_conn.get_connection().close()

# FastAPI 앱 생성
app = FastAPI(
    title="AI Algorithm API with Dual Databases",
    lifespan=lifespan  # lifespan 컨텍스트 매니저 추가
)

# 라우터 등록
app.include_router(metrics_router)
app.include_router(coding_test_router)
app.include_router(resume_router)
app.include_router(interview_router)

# 엔트리 포인트
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)