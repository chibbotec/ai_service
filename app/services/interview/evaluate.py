from typing import List, Dict, Any
from app.schemas.interview import Evaluation
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.mysql.models import Problem, TechInterview, Answer, Participant, Contest, Submit

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

async def evaluate_contest_answers(db: Session, contest_id: int) -> List[Dict[str, Any]]:
    """콘테스트의 모든 답변 평가"""
    try:
        # 문제와 답변 데이터 조회
        problems = await get_problems_data(db, contest_id)
        evaluations = []
        
        # 각 문제의 답변 평가
        for problem in problems:
            for answer in problem['answers']:
                try:
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
                    print(f"답변 평가 중 오류 발생: {str(e)}")
                    continue
        
        # 모든 평가가 완료되면 콘테스트 상태 업데이트
        await update_contest_status(db, contest_id)
        
        return evaluations
        
    except Exception as e:
        print(f"콘테스트 평가 중 오류 발생: {str(e)}")
        raise e
