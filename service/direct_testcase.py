# # app/service/direct_testcase.py
# import time
# import json
# from typing import Dict, List, Any
# from schemas import TestCaseAnswer, TestCaseInput
# from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv

# # 환경변수 로드
# load_dotenv()

# # 프롬프트 템플릿 생성
# template = """당신은 프로그래밍 문제의 테스트 케이스를 생성하는 전문가입니다.
# 다음 프로그래밍 문제에 대한 테스트 케이스 10개를 생성해주세요.

# ### 문제 설명
# {problem_description}

# ### 입력 형식
# {input_description}

# ### 출력 형식
# {output_description}

# ### 예시 솔루션 ({solution_language})
# {solution_code}
# ### 테스트 케이스 유형
# {test_case_types}

# ### 특별 요구사항
# {additional_requirements}

# 테스트 케이스를 생성할 때 다음 지침을 따라주세요:
# 1. 기본 케이스, 경계 케이스, 특수 케이스를 포함시켜 주세요.
# 2. 각 테스트 케이스는 입력(.in)과 출력(.out)으로 구성되어야 합니다.
# 3. 정확히 10개의 테스트 케이스를 생성해주세요.
# 4. 프로그램의 정확성을 검증할 수 있는 다양한 입력을 포함해주세요.
# 5. 테스트 케이스의 이름은 1.in, 1.out, 2.in, 2.out 등의 형식으로 지정해주세요.

# 다음 형식의 JSON으로 응답해주세요:
# {{
#   "testcases": [
#     {{
#       "1.in": "테스트 케이스 1 입력",
#       "1.out": "테스트 케이스 1 출력"
#     }},
#     {{
#       "2.in": "테스트 케이스 2 입력",
#       "2.out": "테스트 케이스 2 출력"
#     }},
#     ...
#   ]
# }}

# 반드시 JSON 형식으로 응답해주세요. 추가 설명이나 텍스트는 포함하지 마세요.
# """

# # 프롬프트 템플릿 설정
# prompt = PromptTemplate(
#     template=template,
#     input_variables=["problem_description", "input_description", "output_description", 
#                     "solution_language", "solution_code", "test_case_types", "additional_requirements"]
# )

# # LLM 모델 설정
# llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o")

# # 체인 구성 (파서 없이 직접 처리)
# chain = prompt | llm

# # 테스트 케이스 생성 함수
# async def generate_test_case_answer_direct(test_input: TestCaseInput) -> TestCaseAnswer:
#     """
#     프로그래밍 문제에 대한 테스트 케이스 생성 (직접 처리 방식)

#     Args:
#         test_input: 문제 설명, 입력 형식, 출력 형식, 예시 솔루션 등을 포함한 입력 데이터

#     Returns:
#         TestCaseAnswer: 생성된 테스트 케이스 목록
#     """
#     start_time = time.time()

#     try:
#         # 추가 요구사항 생성
#         additional_requirements = "특별 판정 필요: " + ("예" if test_input.spj else "아니오")
        
#         # 솔루션 언어와 코드 추출
#         solution_language = test_input.sample_solution.get("language", "")
#         solution_code = test_input.sample_solution.get("code", "")
        
#         # 테스트 케이스 유형 문자열로 변환
#         test_case_types_str = ", ".join(test_input.test_case_types)
        
#         # LLM 직접 호출
#         response = chain.invoke({
#             "problem_description": test_input.problem_description,
#             "input_description": test_input.input_description,
#             "output_description": test_input.output_description,
#             "solution_language": solution_language,
#             "solution_code": solution_code,
#             "test_case_types": test_case_types_str,
#             "additional_requirements": additional_requirements
#         })
        
#         # LLM 응답에서 JSON 추출 (응답은 문자열)
#         response_text = response.content if hasattr(response, 'content') else str(response)
        
#         # JSON 시작과 끝 부분 찾기 (LLM이 추가 설명을 덧붙일 수 있음)
#         json_start = response_text.find('{')
#         json_end = response_text.rfind('}') + 1
        
#         if json_start >= 0 and json_end > json_start:
#             json_str = response_text[json_start:json_end]
#             # JSON 파싱
#             try:
#                 result_dict = json.loads(json_str)
#                 # 결과에 testcases 키가 있는지 확인
#                 if "testcases" in result_dict:
#                     testcase_answer = TestCaseAnswer(testcases=result_dict["testcases"])
#                     processing_time = time.time() - start_time
#                     print(f"테스트 케이스 생성 시간: {processing_time:.2f}초")
#                     return testcase_answer
#                 else:
#                     # testcases 키가 없으면 수동으로 추가
#                     return TestCaseAnswer(testcases=[result_dict])
#             except json.JSONDecodeError as e:
#                 print(f"JSON 파싱 오류: {str(e)}")
#                 print(f"파싱하려던 문자열: {json_str}")
#                 # 기본 응답 생성
#                 return TestCaseAnswer(testcases=[{"error": "JSON 파싱 실패"}])
#         else:
#             print("응답에서 JSON 형식을 찾을 수 없습니다.")
#             print(f"전체 응답: {response_text}")
#             return TestCaseAnswer(testcases=[{"error": "응답에서 JSON을 찾을 수 없음"}])
        
#     except Exception as e:
#         # 오류 발생 시 로깅 및 예외 전파
#         print(f"Error generating test cases: {str(e)}")
#         raise e