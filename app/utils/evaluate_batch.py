from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.mysql.models import Answer
import logging
import asyncio

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self, db: Session, batch_size: int):
        self.db = db
        self.batch_size = batch_size
        self.batch = []
        self.lock = asyncio.Lock()

    async def add_to_batch(self, item: Dict[str, Any]):
        async with self.lock:
            self.batch.append(item)
            if len(self.batch) >= self.batch_size:
                await self.process_batch()

    async def process_batch(self):
        if not self.batch:
            return

        batch_to_process = self.batch.copy()
        self.batch = []

        try:
            for item in batch_to_process:
                answer = self.db.query(Answer).filter(
                    Answer.problem_id == item['problem_id'],
                    Answer.participant_id == item['participant_id']
                ).first()
                
                if answer:
                    answer.rank_score = item['score']
                    answer.feedback = item['feedback']
            
            self.db.commit()
            logger.info(f"배치 업데이트 성공 - {len(batch_to_process)}개 항목")
        except Exception as e:
            self.db.rollback()
            logger.error(f"배치 업데이트 실패: {str(e)}")
            await self._handle_failed_batch(batch_to_process)

    async def _handle_failed_batch(self, failed_batch: List[Dict[str, Any]]):
        for item in failed_batch:
            try:
                await update_evaluation(
                    db=self.db,
                    problem_id=item['problem_id'],
                    participant_id=item['participant_id'],
                    score=item['score'],
                    feedback=item['feedback']
                )
            except Exception as e:
                logger.error(f"개별 업데이트 실패: 문제 ID {item['problem_id']}, 참가자 ID {item['participant_id']}, 오류: {str(e)}")