from fastapi import APIRouter, HTTPException, Depends
from app.schemas.interview import InterviewQuestionInput, InterviewAnswer
from app.services.interview.interview import generate_interview_answer
from app.services.interview.evaluate import evaluate_contest_answers
from app.db.mysql.session import get_db
from app.db.repositories.mysql.tech_interview_repository import TechInterviewRepository
from app.db.mysql.models import TechInterview, Contest, Participant, Answer, Problem, Submit
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["interview"]
)

@router.post("/{space_id}/questions/ai-answer", response_model=InterviewAnswer)
async def create_ai_interview_answer(space_id: int, question_input: InterviewQuestionInput, db: Session = Depends(get_db)):
    try:
        # 클라이언트에서 전달받은 데이터 사용
        question_text = question_input.questionText
        tech_class = question_input.techClass
        question_id = question_input.id

        print(f"Processing request - Question ID: {question_id}, Tech Class: {tech_class}")

        # AI 답변 생성 및 저장
        answer = await generate_interview_answer(tech_class, question_text, question_id, db)
        return answer
    except ValueError as ve:
        print(f"Question not found: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(f"AI answer generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 답변 생성 오류: {str(e)}")

@router.get("/{space_id}/contest/{contest_id}/evaluate")
async def evaluate_contest(
    space_id: int,
    contest_id: int,
    db: Session = Depends(get_db)
):
    try:
        print(f"대회 채점 요청: 대회 ID={contest_id}, 스페이스 ID={space_id}")
        
        # 대회 정보 조회
        contest = db.query(Contest).filter(
            Contest.id == contest_id,
            Contest.space_id == space_id
        ).first()
        
        if not contest:
            raise HTTPException(status_code=404, detail="대회를 찾을 수 없습니다.")
        
        # 평가 실행
        evaluations = await evaluate_contest_answers(db, contest_id)
        
        return {
            "status": "success",
            "message": "평가가 완료되었습니다.",
            "data": {
                "contest_id": contest_id,
                "submit": contest.submit_status.name if contest.submit_status else None,
                "evaluations": evaluations
            }
        }
        
    except Exception as e:
        print(f"평가 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
