from typing import List, Dict, Any
from app.db.redis.connection import RedisConnection
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

redis_conn = RedisConnection()

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
    

@dramatiq.actor(store_results=True)
def evaluate_single_answer(problem_id: int, participant_id: int, 
                         question: str, ai_answer: str, participant_answer: str):
    """개별 답변 평가를 위한 Dramatiq 액터"""
    try:
        logger.info(f"[Worker] 답변 평가 시작 - 문제ID: {problem_id}, 참가자ID: {participant_id}")
        start_time = time.time()
        
        evaluation = chain.invoke({
            "problem": question,
            "ai_answer": ai_answer,
            "participant_answer": participant_answer
        })
        
        # DB 연결 정보를 환경 변수에서 가져오기
        db_host = os.getenv('DB_HOST', '172.30.1.23')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'chibbo_interview')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        
        # DB URL 생성
        db_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"[Worker] DB 연결 시도 - Host: {db_host}")
        
        # DB 세션 생성 및 결과 저장
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        try:
            answer = db.query(Answer).filter(
                Answer.problem_id == problem_id,
                Answer.participant_id == participant_id
            ).first()
            
            if answer:
                answer.rank_score = evaluation.score
                answer.feedback = evaluation.feedback
                db.commit()
                logger.info(f"[Worker] DB 저장 완료 - 문제ID: {problem_id}, 참가자ID: {participant_id}")
            else:
                logger.warning(f"[Worker] 답변을 찾을 수 없음 - 문제ID: {problem_id}, 참가자ID: {participant_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"[Worker] DB 저장 실패 - 문제ID: {problem_id}, 참가자ID: {participant_id}: {str(e)}")
            raise e
        finally:
            db.close()
        
        duration = time.time() - start_time
        logger.info(f"[Worker] 답변 평가 완료 - 문제ID: {problem_id}, 참가자ID: {participant_id}, 소요시간: {duration:.2f}초")
        
        return {
            'problem_id': problem_id,
            'participant_id': participant_id,
            'evaluation': evaluation.dict()
        }
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="parallel",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"[Worker] 답변 평가 중 오류 발생 - 문제ID: {problem_id}, 참가자ID: {participant_id}: {str(e)}")
        raise e

async def evaluate_contest_answers_parallel(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """Dramatiq를 사용한 병렬 처리 방식으로 평가를 수행"""
    try:
        start_time = time.time()
        problems = await get_problems_data(db, contest_id)
        message_ids = []
        
        total_answers = sum(len(p['answers']) for p in problems)
        logger.info(f"[Parallel] 평가 시작 - 총 {len(problems)}개 문제, {total_answers}개 답변")
        
        # 모든 평가 작업을 큐에 추가
        for problem in problems:
            for answer in problem['answers']:
                update_system_metrics('parallel')

                message = evaluate_single_answer.send(
                    problem_id=problem['id'],
                    participant_id=answer['participant_id'],
                    question=problem['question'],
                    ai_answer=problem['ai_answer'],
                    participant_answer=answer['answer']
                )
                message_ids.append(message.message_id)
                logger.info(f"[Parallel] 평가 작업 큐에 추가 - Message ID: {message.message_id}")
        
        # 모든 메시지가 완료될 때까지 대기
        for message_id in message_ids:
            try:
                # 메시지 상태 확인
                broker = dramatiq.get_broker()
                message = broker.get_message(message_id)
                if message:
                    message.wait()
                    logger.info(f"[Parallel] 평가 작업 완료 - Message ID: {message_id}")
                else:
                    logger.error(f"[Parallel] 메시지를 찾을 수 없음 - Message ID: {message_id}")
            except Exception as e:
                logger.error(f"[Parallel] 메시지 완료 대기 중 오류 발생 - Message ID: {message_id}: {str(e)}")
                continue
        
        duration = time.time() - start_time
        EVALUATION_DURATION.labels(method="parallel").observe(duration)
        EVALUATION_COUNTER.labels(method="parallel", status="success").inc(len(message_ids))
        
        logger.info(f"[Parallel] 평가 완료 - 소요시간: {duration:.2f}초, 성공: {len(message_ids)}개")
        
        await update_contest_status(db, contest_id)
        return [{"status": "completed"} for _ in message_ids]
        
    except Exception as e:
        EVALUATION_ERROR_COUNTER.labels(
            method="parallel",
            error_type=type(e).__name__
        ).inc()
        logger.error(f"[Parallel] 콘테스트 평가 중 오류 발생: {str(e)}")
        raise e
