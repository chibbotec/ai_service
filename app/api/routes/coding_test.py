from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.coding_test import TestCaseInput, TestCaseAnswer, TestCaseRequest
from app.services.coding_test.testcase import generate_test_case_answer
from app.services.coding_test.testcase_zip import create_simple_test_case_zip

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["coding_test"]
)

@router.post("/{space_id}/problems/{testCaseId}/generate-testcases", response_model=TestCaseAnswer)
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

@router.post("/{space_id}/problems/{test_case_id}/save-testcases")
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