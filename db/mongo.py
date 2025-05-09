# app/db/mongo.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv(verbose=True)  # verbose=True를 추가하여 로드되는 환경 변수를 확인

# MongoDB 연결 설정
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

print("=== MongoDB 설정 확인 ===")
print(f"환경 변수 MONGO_URI: {MONGO_URI}")
print(f"환경 변수 MONGO_DB_NAME: {DB_NAME}")
print("=====================")

# MongoDB 클라이언트 생성
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 컬렉션 정의 부분에 추가
questions = db.questions

async def check_db_connection():
    """MongoDB 연결 상태 확인"""
    try:
        print(f"MongoDB 연결 시도... URI: {MONGO_URI}")
        # MongoDB 클라이언트의 ping 명령 실행
        client.admin.command('ping')
        print(f"MongoDB 연결 성공! 데이터베이스: {DB_NAME}")
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")
        print("MongoDB가 실행 중인지 확인해주세요.")
        raise
# 함수 추가
async def get_question_by_id(question_id):
  """질문 ID로 질문 조회"""
  from bson.objectid import ObjectId
  return questions.find_one({"_id": ObjectId(question_id)})

async def get_questions_by_space_id(space_id, limit=100):
  """공간 ID로 질문 목록 조회"""
  cursor = questions.find({"spaceId": space_id}).sort("createdAt", -1).limit(limit)
  return [doc for doc in cursor]

async def update_question(question_id, update_data):
  """질문 업데이트 (AI 답변 저장 등)"""
  from bson.objectid import ObjectId
  result = questions.update_one(
      {"_id": ObjectId(question_id)},
      {"$set": update_data}
  )
  return result.modified_count > 0

# app/db/mongo.py에 함수 추가
async def add_ai_answer(question_id, ai_answer):
  
  """질문에 AI 답변 추가"""
  print("AI 답변 저장 요청 받음...")
  from bson.objectid import ObjectId
  result = questions.update_one(
      {"_id": ObjectId(question_id)},
      {"$set": {"answers.ai": ai_answer, "updatedAt": datetime.utcnow()}}
  )
  print("AI 답변 저장 완료!")
  if result.modified_count == 0:
    # 업데이트된 문서가 없으면 예외 발생
    raise RuntimeError(f"질문을 찾을 수 없습니다: {question_id}")
  return questions.find_one({"_id": ObjectId(question_id)})