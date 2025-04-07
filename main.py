# app/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from schemas import InterviewQuestionInput, InterviewAnswer, TestCaseInput, TestCaseAnswer, TestCaseRequest
from service.interview import generate_interview_answer
from service.testcase import generate_test_case_answer
from service.testcase_zip import create_simple_test_case_zip

from db.mongo import add_ai_answer

# FastAPI 앱 생성
app = FastAPI(title="AI Algorithm API with Dual Databases")

# CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:9000", "http://api.chibbotec.kknaks.site"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 헬스 체크 엔드포인트 추가
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

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

        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 답변 생성 오류: {str(e)}")
  
# AI test case 생성 엔드포인트
@app.post("/api/v1/ai/{space_id}/problems/{testCaseId}/generate-testcases", response_model=TestCaseAnswer)
async def generate_test_case(question_input: TestCaseInput):
    try:
        # AI 테스트 케이스 생성
        print("테스트 케이스 생성 요청 받음...")
        print(f"문제: {question_input.problem_description[:50]}...")

        print(" 테스트 케이스를 생성합니다.")
        test_case = await generate_test_case_answer(question_input)
        
        print("테스트 케이스 생성 완료!")
        print(f"생성된 테스트 케이스: {test_case}")
        return test_case
    except Exception as e:
        print(f"테스트 케이스 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 테스트 케이스 생성 오류: {str(e)}")

@app.post("/api/v1/ai/{space_id}/problems/{test_case_id}/save-testcases")
async def generate_test_cases_zip(space_id: str, test_case_id: str, request: TestCaseRequest):
    try:
        print(f"테스트 케이스 ZIP 생성 요청: ID={test_case_id}, 테스트케이스 수={len(request.testcases)}")
        # ZIP 파일 생성
        zip_path = await create_simple_test_case_zip(test_case_id, request.testcases)
        print(f"테스트 케이스 zip 생성완료 {zip_path}")
        # 파일 응답 반환
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"testcase_{test_case_id}.zip"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZIP 파일 생성 중 오류: {str(e)}")


# 엔트리 포인트
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)