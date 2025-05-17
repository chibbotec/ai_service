from datetime import datetime
from typing import Dict, List, Any, Optional
from app.db.mongodb.models import QUESTION_SCHEMA

class QuestionRepository:
    def __init__(self, db):
        self.collection = db.questions

    async def get_question_by_id(self, question_id: str) -> Dict:
        """질문 ID로 질문 조회"""
        return self.collection.find_one({"_id": question_id})

    async def get_questions_by_space_id(self, space_id: int, limit: int = 100) -> List[Dict]:
        """공간 ID로 질문 목록 조회"""
        return list(self.collection.find({"spaceId": space_id}).limit(limit))

    async def update_question(self, question_id: str, update_data: Dict) -> Dict:
        """질문 업데이트"""
        result = self.collection.update_one(
            {"_id": question_id},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise RuntimeError(f"Question ID {question_id} not found")
        return await self.get_question_by_id(question_id)

    async def add_ai_answer(self, question_id: str, ai_answer: str) -> Dict:
        """질문에 AI 답변 추가"""
        update_data = {
            "answers.ai": ai_answer,
            "updatedAt": datetime.utcnow()
        }
        return await self.update_question(question_id, update_data) 