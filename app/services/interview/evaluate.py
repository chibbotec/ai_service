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
from app.chain.evaluate_chain import chain
from app.db.mysql.connection import DB_CONFIG
from app.config.evaluation_config import EVALUATION_CONFIG
from app.utils.evaluate_batch import BatchProcessor
from app.utils.progress_tracker import ProgressTracker
from app.tasks.evaluation_task import EvaluationTask
from app.services.interview.evaluation_core import evaluate_answer

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
    try:
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        
        # 컴포넌트 초기화
        sem = asyncio.Semaphore(EVALUATION_CONFIG['CONCURRENT_LIMIT'])
        batch_processor = BatchProcessor(db, EVALUATION_CONFIG['BATCH_SIZE'])
        progress_tracker = ProgressTracker(
            total=sum(len(p['answers']) for p in problems),
            log_interval=EVALUATION_CONFIG['LOG_INTERVAL']
        )
        evaluation_task = EvaluationTask(sem, batch_processor, progress_tracker)
        
        # 작업 생성 및 실행
        tasks = []
        for problem in problems:
            for answer in problem['answers']:
                task_data = {
                    'problem_id': problem['id'],
                    'participant_id': answer['participant_id'],
                    'nickname': answer['nickname'],
                    'question': problem['question'],
                    'ai_answer': problem['ai_answer'],
                    'participant_answer': answer['answer']
                }
                tasks.append(evaluation_task.execute(task_data))
        
        # 결과 수집 및 처리
        results = await asyncio.gather(*tasks)
        await batch_processor.process_batch()  # 남은 배치 처리
        
        successful_evaluations = [r for r in results if r['status'] == 'success']
        
        # 메트릭 업데이트
        duration = time.time() - start_time
        EVALUATION_DURATION.labels(method="parallel").observe(duration)
        EVALUATION_COUNTER.labels(method="parallel", status="success").inc(len(successful_evaluations))
        EVALUATION_COUNTER.labels(method="parallel", status="error").inc(len(results) - len(successful_evaluations))
        
        await update_contest_status(db, contest_id)
        return successful_evaluations
        
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="parallel",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"콘테스트 평가 중 오류 발생: {str(e)}", exc_info=True)
        raise e

async def evaluate_contest_answers_parallel_1(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """고급 병렬 처리 기능을 갖춘 평가 함수
    - 진행상황 추적
    - 배치 처리
    - 적응형 속도 제어
    - 재시도 메커니즘
    """
    try:
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        
        # 설정 매개변수
        CONCURRENT_LIMIT = DB_CONFIG['CONCURRENT_LIMIT']
        BATCH_SIZE = DB_CONFIG['BATCH_SIZE']
        MAX_RETRIES = DB_CONFIG['MAX_RETRIES']
        
        # 세마포어 및 공유 상태
        sem = asyncio.Semaphore(CONCURRENT_LIMIT)
        progress = {"total": 0, "completed": 0, "success": 0, "failed": 0}
        
        # 진행 상황 추적용 잠금
        lock = asyncio.Lock()
        db_batch = []  # 배치 업데이트를 위한 목록
        
        # 총 작업 수 계산
        total_answers = sum(len(p['answers']) for p in problems)
        progress["total"] = total_answers
        
        logger.info(f"[Advanced] 평가 시작 - 총 {len(problems)}개 문제, {total_answers}개 답변")
        update_system_metrics('advanced_parallel')
        
        # 배치 DB 업데이트 함수
        async def process_batch():
            nonlocal db_batch
            
            if not db_batch:
                return
                
            batch_to_process = db_batch.copy()
            db_batch = []
            
            try:
                # 트랜잭션으로 한 번에 처리
                for item in batch_to_process:
                    answer = db.query(Answer).filter(
                        Answer.problem_id == item['problem_id'],
                        Answer.participant_id == item['participant_id']
                    ).first()
                    
                    if answer:
                        answer.rank_score = item['score']
                        answer.feedback = item['feedback']
                
                db.commit()
                logger.info(f"[Advanced] 배치 업데이트 성공 - {len(batch_to_process)}개 항목")
            except Exception as e:
                db.rollback()
                logger.error(f"[Advanced] 배치 업데이트 실패: {str(e)}")
                
                # 실패한 배치는 개별적으로 다시 시도
                for item in batch_to_process:
                    try:
                        await update_evaluation(
                            db=db,
                            problem_id=item['problem_id'],
                            participant_id=item['participant_id'],
                            score=item['score'],
                            feedback=item['feedback']
                        )
                    except Exception as inner_e:
                        logger.error(f"[Advanced] 개별 업데이트 실패: 문제 ID {item['problem_id']}, 참가자 ID {item['participant_id']}, 오류: {str(inner_e)}")
        
        # 진행 상황 업데이트 함수
        async def update_progress(status):
            async with lock:
                progress["completed"] += 1
                if status == "success":
                    progress["success"] += 1
                else:
                    progress["failed"] += 1
                
                # 진행 상황 로깅 (10% 단위)
                percent = (progress["completed"] / progress["total"]) * 100
                if percent % 10 < 0.5 and percent > 0:  # 10% 단위로 로깅
                    logger.info(f"[Advanced] 진행 상황: {progress['completed']}/{progress['total']} ({percent:.1f}%), 성공: {progress['success']}, 실패: {progress['failed']}")
        
        # 평가 작업 수행 함수 (재시도 로직 포함)
        async def evaluate_task_with_retry(task_data):
            retries = 0
            while retries <= MAX_RETRIES:
                try:
                    async with sem:
                        # 평가 작업 수행
                        evaluation = await evaluate_answer(
                            problem=task_data['question'],
                            ai_answer=task_data['ai_answer'],
                            participant_answer=task_data['participant_answer']
                        )
                        
                        # 결과를 배치에 추가
                        async with lock:
                            db_batch.append({
                                'problem_id': task_data['problem_id'],
                                'participant_id': task_data['participant_id'],
                                'score': evaluation.score,
                                'feedback': evaluation.feedback
                            })
                            
                            # 배치 크기에 도달하면 DB 업데이트
                            if len(db_batch) >= BATCH_SIZE:
                                await process_batch()
                        
                        await update_progress("success")
                        
                        return {
                            'status': 'success',
                            'problem_id': task_data['problem_id'],
                            'participant_id': task_data['participant_id'],
                            'nickname': task_data.get('nickname', ''),
                            'evaluation': evaluation.dict()
                        }
                except Exception as e:
                    retries += 1
                    if retries <= MAX_RETRIES:
                        wait_time = 2 ** retries  # 지수 백오프
                        logger.warning(f"[Advanced] 평가 재시도 ({retries}/{MAX_RETRIES}) - 문제 ID: {task_data['problem_id']}, 참가자 ID: {task_data['participant_id']}, {wait_time}초 후 재시도")
                        await asyncio.sleep(wait_time)
                    else:
                        EVALUATION_ERROR_COUNTER.labels(
                            method="advanced_parallel",
                            error_type=type(e).__name__
                        ).inc()
                        logger.error(f"[Advanced] 평가 실패 (최대 재시도 횟수 초과) - 문제 ID: {task_data['problem_id']}, 참가자 ID: {task_data['participant_id']}, 오류: {str(e)}")
                        
                        await update_progress("failed")
                        
                        return {
                            'status': 'error',
                            'problem_id': task_data['problem_id'],
                            'participant_id': task_data['participant_id'],
                            'error': str(e)
                        }
        
        # 모든 작업을 태스크 목록으로 생성
        tasks = []
        for problem in problems:
            for answer in problem['answers']:
                task_data = {
                    'problem_id': problem['id'],
                    'participant_id': answer['participant_id'],
                    'nickname': answer['nickname'],
                    'question': problem['question'],
                    'ai_answer': problem['ai_answer'],
                    'participant_answer': answer['answer']
                }
                tasks.append(evaluate_task_with_retry(task_data))
        
        # 모든 작업을 병렬로 실행하고 결과 수집
        results = await asyncio.gather(*tasks)
        
        # 남은 배치 처리
        await process_batch()
        
        # 성공한 결과만 필터링
        successful_evaluations = [
            result for result in results 
            if result['status'] == 'success'
        ]
        
        # 메트릭 업데이트
        duration = time.time() - start_time
        EVALUATION_DURATION.labels(method="advanced_parallel").observe(duration)
        EVALUATION_COUNTER.labels(method="advanced_parallel", status="success").inc(len(successful_evaluations))
        EVALUATION_COUNTER.labels(method="advanced_parallel", status="error").inc(len(results) - len(successful_evaluations))
        
        success_rate = (len(successful_evaluations) / len(results)) * 100 if results else 0
        logger.info(f"[Advanced] 평가 완료 - 소요시간: {duration:.2f}초, 성공: {len(successful_evaluations)}/{len(results)} ({success_rate:.1f}%), 처리량: {total_answers/duration:.1f}개/초")
        
        # 대회 상태 업데이트
        await update_contest_status(db, contest_id)
        
        return successful_evaluations
        
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="advanced_parallel",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"[Advanced] 콘테스트 평가 중 오류 발생: {str(e)}", exc_info=True)
        raise e