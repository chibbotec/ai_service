from typing import Dict, Any
import asyncio
import logging
from app.config.evaluation_config import EVALUATION_CONFIG
from app.utils.progress_tracker import ProgressStatus
from app.services.interview.evaluation_core import evaluate_answer

logger = logging.getLogger(__name__)

class EvaluationTask:
    def __init__(self, semaphore: asyncio.Semaphore, batch_processor, progress_tracker):
        self.semaphore = semaphore
        self.batch_processor = batch_processor
        self.progress_tracker = progress_tracker
        self.max_retries = EVALUATION_CONFIG['MAX_RETRIES']
        self.retry_base_delay = EVALUATION_CONFIG['RETRY_BASE_DELAY']

    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        retries = 0
        while retries <= self.max_retries:
            try:
                async with self.semaphore:
                    evaluation = await evaluate_answer(
                        problem=task_data['question'],
                        ai_answer=task_data['ai_answer'],
                        participant_answer=task_data['participant_answer']
                    )
                    
                    await self.batch_processor.add_to_batch({
                        'problem_id': task_data['problem_id'],
                        'participant_id': task_data['participant_id'],
                        'score': evaluation.score,
                        'feedback': evaluation.feedback
                    })
                    
                    await self.progress_tracker.update(ProgressStatus.SUCCESS)
                    
                    return {
                        'status': 'success',
                        'problem_id': task_data['problem_id'],
                        'participant_id': task_data['participant_id'],
                        'nickname': task_data.get('nickname', ''),
                        'evaluation': evaluation.dict()
                    }
            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    wait_time = self.retry_base_delay ** retries
                    logger.warning(
                        f"평가 재시도 ({retries}/{self.max_retries}) - "
                        f"문제 ID: {task_data['problem_id']}, "
                        f"참가자 ID: {task_data['participant_id']}, "
                        f"{wait_time}초 후 재시도"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    await self.progress_tracker.update(ProgressStatus.FAILED)
                    return {
                        'status': 'error',
                        'problem_id': task_data['problem_id'],
                        'participant_id': task_data['participant_id'],
                        'error': str(e)
                    }