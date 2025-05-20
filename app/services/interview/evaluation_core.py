from app.schemas.interview import Evaluation
from app.chain.evaluate_chain import chain
import logging

logger = logging.getLogger(__name__)

async def evaluate_answer(problem: str, ai_answer: str, participant_answer: str) -> Evaluation:
    """개별 답변 평가"""
    try:
        response = chain.invoke({
            "problem": problem,
            "ai_answer": ai_answer,
            "participant_answer": participant_answer
        })
        return response
    except Exception as e:
        logger.error(f"답변 평가 중 오류 발생: {str(e)}")
        raise e 