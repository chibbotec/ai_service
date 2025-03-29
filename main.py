# app/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 이 부분이 누락됨
from schemas import InterviewQuestionInput, InterviewAnswer
from service.services import generate_interview_answer
from db.mongo import add_ai_answer

# FastAPI 앱 생성
app = FastAPI(title="AI Algorithm API with Dual Databases")

# CORS 설정
app.add_middleware(
    CORSMiddleware,  # 미들웨어 클래스를 첫 번째 인자로 추가
    allow_origins=["http://localhost:9000"],  # 실제 환경에서는 구체적인 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI 면접 답변 생성 엔드포인트
@app.post("/api/v1/ai/{space_id}/questions/ai-answer", response_model=InterviewAnswer)
async def create_ai_interview_answer(space_id: int, question_input: InterviewQuestionInput):
  try:
    # 클라이언트에서 전달받은 데이터 사용
    question_text = question_input.questionText
    tech_class = question_input.techClass
    question_id = question_input.questionId

    # AI 답변 생성
    answer = await generate_interview_answer(tech_class, question_text)

    # MongoDB에 AI 답변 저장
    try:
      updated_question = await add_ai_answer(
          question_id,
          answer.model_dump_json()
      )
    except RuntimeError as e:
      # 질문 ID가 유효하지 않은 경우, 오류만 로깅하고 답변은 반환
      print(f"답변 저장 실패: {str(e)}")
      # 선택적으로 비동기 작업으로 오류 로깅 추가 가능
      # await save_log(...)

    return answer
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"AI 답변 생성 오류: {str(e)}")

# 엔트리 포인트
if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)