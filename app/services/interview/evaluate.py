from typing import List, Dict, Any
from app.schemas.interview import Evaluation
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.mysql.models import Problem, TechInterview, Answer, Participant, Contest, Submit
import dramatiq
import time
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from app.metrics import (
    EVALUATION_DURATION,
    EVALUATION_COUNTER,
    EVALUATION_ERROR_COUNTER,
    update_system_metrics
)
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# LLM 모델과 파서 초기화
parser = PydanticOutputParser(pydantic_object=Evaluation)

template = """
다음은 기술 면접 문제와 그에 대한 모범답안, 그리고 응시자의 답변입니다.

문제: {problem}

모범답안: {ai_answer}

응시자의 답변: {participant_answer}

위 답변을 평가하여 다음 형식으로 응답해주세요:
{format_instructions}

평가 기준:
1. 핵심 개념의 이해도 (30점)
2. 설명의 정확성과 명확성 (30점)
3. 전문 용어의 적절한 사용 (20점)
4. 답변의 구조와 논리성 (20점)
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["problem", "ai_answer", "participant_answer"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

llm = ChatOpenAI(temperature=0.2, model_name="gpt-4")
chain = prompt | llm | parser

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
    

class EvaluationWorker:
    def __init__(self, worker_id: int, db: Session):
        self.worker_id = worker_id
        self.db = db
        self.is_running = False

    async def process_evaluation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"[Worker {self.worker_id}] 답변 평가 시작 - 문제ID: {task['problem_id']}")
            start_time = time.time()
            
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

    async def add_task(self, task: Dict[str, Any]):
        await self.queue.put(task)

    async def start_workers(self, db: Session):
        self.is_processing = True
        self.workers = [
            EvaluationWorker(i, db) for i in range(self.num_workers)
        ]
        
        # 워커 시작
        worker_tasks = [
            self._worker_loop(worker) for worker in self.workers
        ]
        
        # 모든 워커가 완료될 때까지 대기
        await asyncio.gather(*worker_tasks)
        self.is_processing = False

    async def _worker_loop(self, worker: EvaluationWorker):
        while self.is_processing:
            try:
                # 큐에서 작업 가져오기
                task = await self.queue.get()
                
                # 작업 처리
                result = await worker.process_evaluation(task)
                self.results.append(result)
                
                # 작업 완료 표시
                self.queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"워커 {worker.worker_id} 오류: {str(e)}")
                continue

    def get_results(self) -> List[Dict[str, Any]]:
        return self.results

async def evaluate_contest_answers_parallel(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """워커와 큐를 사용한 병렬 처리 방식으로 평가를 수행"""
    try:
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        
        # 평가 큐 초기화 (워커 수는 시스템 리소스에 따라 조정)
        evaluation_queue = EvaluationQueue(num_workers=3)
        
        total_answers = sum(len(p['answers']) for p in problems)
        logger.info(f"[Queue] 평가 시작 - 총 {len(problems)}개 문제, {total_answers}개 답변")
        
        # 모든 평가 작업을 큐에 추가
        for problem in problems:
            for answer in problem['answers']:
                update_system_metrics('parallel')
                
                task = {
                    'problem_id': problem['id'],
                    'participant_id': answer['participant_id'],
                    'question': problem['question'],
                    'ai_answer': problem['ai_answer'],
                    'participant_answer': answer['answer']
                }
                await evaluation_queue.add_task(task)
        
        # 워커 시작 및 모든 작업 완료 대기
        await evaluation_queue.start_workers(db)
        
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
