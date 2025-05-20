# app/service/testcase.py
import time
import json
from app.schemas.coding_test import TestCaseAnswer, TestCaseInput
from app.chain import testcase_chain

# 테스트 케이스 생성 함수
async def generate_test_case_answer(test_input: TestCaseInput) -> TestCaseAnswer:
    """
    프로그래밍 문제에 대한 테스트 케이스 생성

    Args:
        test_input: 문제 설명, 입력 형식, 출력 형식, 예시 솔루션 등을 포함한 입력 데이터

    Returns:
        TestCaseAnswer: 생성된 테스트 케이스 목록
    """
    start_time = time.time()

    try:
        # 추가 요구사항 생성
        additional_requirements = "특별 판정 필요: " + ("예" if test_input.spj else "아니오")
        
        # 솔루션 언어와 코드 추출
        solution_language = test_input.sample_solution.get("language", "")
        solution_code = test_input.sample_solution.get("code", "")
        
        # 테스트 케이스 유형 문자열로 변환
        test_case_types_str = ", ".join(test_input.test_case_types)
        
        # LangChain 체인 실행
        response = testcase_chain.invoke({
            "problem_description": test_input.problem_description,
            "input_description": test_input.input_description,
            "output_description": test_input.output_description,
            "solution_language": solution_language,
            "solution_code": solution_code,
            "test_case_types": test_case_types_str,
            "additional_requirements": additional_requirements
        })
        
        # 응답에서 content 추출 (LangChain AIMessage 객체에서)
        if hasattr(response, 'content'):
            content = response.content
            # JSON 문자열인 경우 파싱
            if isinstance(content, str):
                try:
                    parsed_content = json.loads(content)
                    # 파싱된 JSON을 TestCaseAnswer로 변환
                    result = TestCaseAnswer.model_validate(parsed_content)
                    return result
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 원본 LLM 응답에서 items 부분 추출 시도
                    print("JSON 파싱 실패, TestCaseAnswer 직접 생성")
                    return TestCaseAnswer(testcases=[{"error": "Failed to parse JSON response"}])
        
        # 이미 dict 형태인 경우
        if isinstance(response, dict):
            # TestCaseAnswer로 변환
            return TestCaseAnswer.model_validate(response)
            
        processing_time = time.time() - start_time
        print(f"테스트 케이스 생성 시간: {processing_time:.2f}초")
        
        return response
    except Exception as e:
        # 오류 발생 시 로깅 및 예외 전파
        print(f"Error generating test cases: {str(e)}")
        raise e