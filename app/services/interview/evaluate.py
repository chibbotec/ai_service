from typing import List, Dict, Any
from app.schemas.interview import Evaluation
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.mysql.models import Problem, TechInterview, Answer, Participant, Contest, Submit
import time
from app.metrics import (
    EVALUATION_DURATION,
    EVALUATION_COUNTER,
    EVALUATION_ERROR_COUNTER,
    update_system_metrics
)
import logging
from app.config.worker import EvaluationQueue
from app.chain.evaluate_chain import chain

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def get_problems_data(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """문제와 답변 데이터 조회"""
    try:
        # 문제와 답변 정보 조회
        problems = db.query(Problem).filter(Problem.contest_id == contest_id).all()
        
        problems_data = []
        for problem in problems:
            tech_interview = problem.tech_interview
            answers = db.query(Answer).filter(
                Answer.problem_id == problem.id
            ).all()
            
            problem_data = {
                'id': problem.id,
                'question': tech_interview.question,
                'ai_answer': tech_interview.ai_answer,
                'tech_class': tech_interview.tech_class_enum.name if tech_interview.tech_class_enum else None,
                'answers': []
            }
            
            for answer in answers:
                participant = answer.participant
                problem_data['answers'].append({
                    'answer_id': answer.id,
                    'participant_id': participant.id,
                    'nickname': participant.nickname,
                    'answer': answer.answer,
                    'feedback': answer.feedback,
                    'rank_score': answer.rank_score
                })
            
            problems_data.append(problem_data)
        
        return problems_data
        
    except Exception as e:
        print(f"문제 데이터 조회 중 오류 발생: {str(e)}")
        raise Exception(f"문제 조회 실패: {str(e)}")

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
        print(f"답변 평가 중 오류 발생: {str(e)}")
        raise e

async def update_evaluation(db: Session, problem_id: int, participant_id: int, score: int, feedback: str):
    """평가 결과를 DB에 업데이트"""
    try:
        answer = db.query(Answer).filter(
            Answer.problem_id == problem_id,
            Answer.participant_id == participant_id
        ).first()
        
        if answer:
            answer.rank_score = score
            answer.feedback = feedback
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"평가 결과 업데이트 실패: {str(e)}")
        raise e

async def update_contest_status(db: Session, contest_id: int):
    """콘테스트 상태를 EVALUATED로 업데이트"""
    try:
        contest = db.query(Contest).filter(Contest.id == contest_id).first()
        if contest:
            contest.submit = 2  # EVALUATED = 2
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"콘테스트 상태 업데이트 실패: {str(e)}")
        raise e

async def evaluate_contest_answers_sequential(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """콘테스트의 모든 답변 평가"""
    try:
        # 문제와 답변 데이터 조회
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        evaluations = []
        
        logger.info(f"[Sequential] 평가 시작 - 총 {len(problems)}개 문제, {sum(len(p['answers']) for p in problems)}개 답변")
        
        # 각 문제의 답변 평가
        for problem in problems:
            for answer in problem['answers']:
                try:
                    update_system_metrics('sequential')

                    evaluation = await evaluate_answer(
                        problem=problem['question'],
                        ai_answer=problem['ai_answer'],
                        participant_answer=answer['answer']
                    )
                    
                    # 평가 결과 저장
                    await update_evaluation(
                        db=db,
                        problem_id=problem['id'],
                        participant_id=answer['participant_id'],
                        score=evaluation.score,
                        feedback=evaluation.feedback
                    )
                    
                    evaluations.append({
                        'problem_id': problem['id'],
                        'participant_id': answer['participant_id'],
                        'nickname': answer['nickname'],
                        'evaluation': evaluation.dict()
                    })
                    
                except Exception as e:
                    EVALUATION_ERROR_COUNTER.labels(
                        method="sequential",
                        error_type=type(e).__name__
                    ).inc()
                    logger.error(f"[Sequential] 답변 평가 중 오류 발생: {str(e)}")
                    continue

        duration = time.time() - start_time
        EVALUATION_DURATION.labels(method="sequential").observe(duration)
        EVALUATION_COUNTER.labels(method="sequential", status="success").inc(len(evaluations))
        
        logger.info(f"[Sequential] 평가 완료 - 소요시간: {duration:.2f}초, 성공: {len(evaluations)}개")
        
        # 모든 평가가 완료되면 콘테스트 상태 업데이트
        await update_contest_status(db, contest_id)
        
        return evaluations
        
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="sequential",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"[Sequential] 콘테스트 평가 중 오류 발생: {str(e)}")
        raise e

async def evaluate_contest_answers_parallel(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """워커와 큐를 사용한 병렬 처리 방식으로 평가를 수행"""
    try:
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        
        # 평가 큐 초기화 (워커 수는 시스템 리소스에 따라 조정)
        evaluation_queue = EvaluationQueue(num_workers=3)
        
        total_answers = sum(len(p['answers']) for p in problems)
        logger.info(f"[Queue] 평가 시작 - 총 {len(problems)}개 문제, {total_answers}개 답변")
        
        # 워커 시작
        worker_task = asyncio.create_task(evaluation_queue.start_workers(db))
        
        # 모든 평가 작업을 큐에 추가 (await 없이)
        for problem in problems:
            for answer in problem['answers']:
                task = {
                    'problem_id': problem['id'],
                    'participant_id': answer['participant_id'],
                    'question': problem['question'],
                    'ai_answer': problem['ai_answer'],
                    'participant_answer': answer['answer']
                }
                evaluation_queue.add_task(task)
        
        # 모든 작업이 완료될 때까지 대기
        await worker_task
        
        # 결과 수집
        evaluations = evaluation_queue.get_results()
        successful_evaluations = [
            eval for eval in evaluations 
            if eval['status'] == 'success'
        ]
        
        duration = time.time() - start_time
        EVALUATION_DURATION.labels(method="parallel").observe(duration)
        EVALUATION_COUNTER.labels(method="parallel", status="success").inc(len(successful_evaluations))
        
        logger.info(f"[Queue] 평가 완료 - 소요시간: {duration:.2f}초, 성공: {len(successful_evaluations)}개")
        
        await update_contest_status(db, contest_id)
        return successful_evaluations
        
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="parallel",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"[Queue] 콘테스트 평가 중 오류 발생: {str(e)}")
        raise e
