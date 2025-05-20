import asyncio
import logging
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.mysql.models import Answer
from app.chain.evaluate_chain import chain
from app.metrics import update_system_metrics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationWorker:
    def __init__(self, worker_id: int, db: Session):
        self.worker_id = worker_id
        self.db = db
        self.is_running = False

    async def process_evaluation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"[Worker {self.worker_id}] 답변 평가 시작 - 문제ID: {task['problem_id']}")
            start_time = time.time()
            
            # 병렬 작업 중 메트릭 업데이트
            update_system_metrics('parallel')
            
            evaluation = chain.invoke({
                "problem": task['question'],
                "ai_answer": task['ai_answer'],
                "participant_answer": task['participant_answer']
            })
            
            # DB에 결과 저장
            answer = self.db.query(Answer).filter(
                Answer.problem_id == task['problem_id'],
                Answer.participant_id == task['participant_id']
            ).first()
            
            if answer:
                answer.rank_score = evaluation.score
                answer.feedback = evaluation.feedback
                self.db.commit()
                logger.info(f"[Worker {self.worker_id}] DB 저장 완료 - 문제ID: {task['problem_id']}")
            else:
                logger.warning(f"[Worker {self.worker_id}] 답변을 찾을 수 없음 - 문제ID: {task['problem_id']}")
            
            duration = time.time() - start_time
            logger.info(f"[Worker {self.worker_id}] 답변 평가 완료 - 소요시간: {duration:.2f}초")
            
            return {
                'problem_id': task['problem_id'],
                'participant_id': task['participant_id'],
                'evaluation': evaluation.dict(),
                'status': 'success'
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"[Worker {self.worker_id}] 평가 실패: {str(e)}")
            return {
                'problem_id': task['problem_id'],
                'participant_id': task['participant_id'],
                'status': 'error',
                'error': str(e)
            }

class EvaluationQueue:
    def __init__(self, num_workers: int = 3):
        self.queue = asyncio.Queue()
        self.workers = []
        self.num_workers = num_workers
        self.results = []
        self.is_processing = False
        self.tasks_added = 0
        self.tasks_completed = 0
        self.worker_tasks = []

    def add_task(self, task: Dict[str, Any]):
        self.tasks_added += 1
        self.queue.put_nowait(task)

    async def start_workers(self, db: Session):
        self.is_processing = True
        self.workers = [EvaluationWorker(i, db) for i in range(self.num_workers)]
        
        # 워커 시작
        self.worker_tasks = [
            asyncio.create_task(self._worker_loop(worker)) 
            for worker in self.workers
        ]
        
        logger.info(f"[Queue] {self.num_workers}개의 워커 시작됨")
        
        # 모든 작업이 완료될 때까지 대기
        while self.tasks_completed < self.tasks_added:
            await asyncio.sleep(0.1)
        
        # 워커 태스크 종료
        for task in self.worker_tasks:
            task.cancel()
        
        try:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        
        self.is_processing = False
        logger.info("[Queue] 모든 워커 종료됨")

    async def _worker_loop(self, worker: EvaluationWorker):
        logger.info(f"[Worker {worker.worker_id}] 시작됨")
        while self.is_processing:
            try:
                # 큐에서 작업 가져오기 (작업이 없으면 대기)
                task = await self.queue.get()
                
                # 작업 처리
                result = await worker.process_evaluation(task)
                self.results.append(result)
                self.tasks_completed += 1
                
                # 작업 완료 표시
                self.queue.task_done()
                
            except asyncio.CancelledError:
                logger.info(f"[Worker {worker.worker_id}] 종료됨")
                break
            except Exception as e:
                logger.error(f"[Worker {worker.worker_id}] 오류: {str(e)}")
                self.tasks_completed += 1
                continue

    def get_results(self) -> List[Dict[str, Any]]:
        return self.results
