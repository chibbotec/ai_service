import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(verbose=True)

class MongoDBConnection:
    def __init__(self):
        self.MONGO_URI = os.getenv("MONGO_URI")
        self.DB_NAME = os.getenv("MONGO_DB_NAME")
        self.client = None
        self.db = None

    def connect(self):
        """MongoDB 연결 설정"""
        print("=== MongoDB 설정 확인 ===")
        print(f"환경 변수 MONGO_URI: {self.MONGO_URI}")
        print(f"환경 변수 MONGO_DB_NAME: {self.DB_NAME}")
        print("=====================")

        self.client = MongoClient(self.MONGO_URI)
        self.db = self.client[self.DB_NAME]
        return self.db

    async def check_connection(self):
        """MongoDB 연결 상태 확인"""
        try:
            print(f"MongoDB 연결 시도... URI: {self.MONGO_URI}")
            # MongoDB 클라이언트의 ping 명령 실행
            self.client.admin.command('ping')
            print(f"MongoDB 연결 성공! 데이터베이스: {self.DB_NAME}")
            return True
        except Exception as e:
            print(f"MongoDB 연결 실패: {e}")
            print("MongoDB가 실행 중인지 확인해주세요.")
            raise

    def close(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
