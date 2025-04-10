# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

# 면접 질문 입력 스키마 (수정됨)
class InterviewQuestionInput(BaseModel):
  """AI 면접 답변 생성을 위한 입력 스키마"""
  questionId: str
  questionText: str  # 질문 내용 추가
  techClass: str = Field(default="Technology")  # 기술 분류 필드 추가

  class Config:
    schema_extra = {
      "example": {
        "questionId": "67de37dc19da0d630ff94a1b",
        "questionText": "MongoDB의 인덱싱에 대해 설명해주세요.",
        "techClass": "Database"
      }
    }

# 면접 답변 출력 스키마
class InterviewAnswer(BaseModel):
  """면접 질문에 대한 AI 답변 스키마"""
  question: str = Field(description="면접에서 질문받은 내용")
  answer: str = Field(description="면접 질문에 대한 모범 답변")
  tips: str = Field(description="면접에서 이 답변을 할 때 강조할 포인트")
  related_topics: str = Field(description="관련 기술/개념 추가 설명")

  class Config:
    schema_extra = {
      "example": {
        "question": "몽고DB에 대해 어떻게 생각하세요?",
        "answer": "MongoDB는 문서 지향 NoSQL 데이터베이스로, JSON과 유사한 BSON 형식으로 데이터를 저장합니다...",
        "tips": "실제 프로젝트에서 MongoDB를 사용한 경험과 관계형 DB와의 비교 분석을 언급하면 좋습니다.",
        "related_topics": "NoSQL, 문서 데이터베이스, 스키마리스 설계, 샤딩, 레플리카셋"
      }
    }

class TestCaseInput(BaseModel):
  """AI 테스트 케이스 생성을 위한 입력 스키마"""
  problem_description: str = Field(description="문제 설명")
  input_description: str = Field(description="입력 형식 설명")
  output_description: str = Field(description="출력 형식 설명")
  sample_solution: dict = Field(description="예시 솔루션 (언어와 코드)")
  selected_languages: list[str] = Field(description="선택된 프로그래밍 언어들")
  spj: bool = Field(description="특별한 판정이 필요한지 여부", default=False)
  test_case_types: list[str] = Field(
    description="""테스트 케이스 유형 선택:
    - basic: 문제 예시와 유사한 기본 테스트 케이스
    - boundary: 최소, 최대 값 등의 경계 조건 케이스
    - special: 예외 상황이나 특별한 패턴 케이스
    - large: 성능 테스트를 위한 대용량 데이터 케이스""",
    default=["basic"]
  )

  class Config:
    schema_extra = {
      "example": {
        "problem_description": "N개의 숫자를 정렬하는 문제입니다.",
        "input_description": "첫 줄에 N개의 숫자가 주어집니다.",
        "output_description": "N개의 숫자를 오름차순으로 정렬하여 출력합니다.",
        "sample_solution": {
          "language": "C",
          "code": "int main() { /* 코드 내용 */ }"
        },
        "selected_languages": ["C", "C++", "Python"],
        "spj": False,
        "test_case_types": ["basic", "boundary", "special", "large"]
      }
    }

# 테스트 케이스 항목 스키마 - 각 테스트 케이스는 딕셔너리 형태로 저장됨
class TestCase(BaseModel):
  """개별 테스트 케이스"""
  # 동적 필드를 허용하는 자유 형식 딕셔너리 (1.in, 1.out 등의 키를 가짐)
  pass

class TestCaseAnswer(BaseModel):
    """AI 테스트 케이스 생성 결과 스키마"""
    testcases: List[Dict[str, str]] = Field(description="테스트 케이스 목록")

    class Config:
        schema_extra = {
            "example": {
                "testcases": [
                    {
                        "1.in": "5\n1 3 5 7 9\n",
                        "1.out": "1 3 5 7 9\n"
                    },
                    {
                        "2.in": "5\n9 7 5 3 1\n",
                        "2.out": "1 3 5 7 9\n"
                    }
                ]
            }
        }
    
    # Pydantic v2 스타일의 모델 설정 및 검증
    @classmethod
    def model_validate(cls, obj):
        """복잡한 JSON 구조에서 testcases 필드 추출"""
        if isinstance(obj, dict):
            # properties.testcases.items 형태 처리
            if "properties" in obj and "testcases" in obj["properties"]:
                if "items" in obj["properties"]["testcases"]:
                    return super().model_validate({"testcases": obj["properties"]["testcases"]["items"]})
            
            # 기본 testcases 키가 있는 경우
            if "testcases" in obj:
                return super().model_validate(obj)
            
            # 다른 모든 경우, 빈 목록 생성
            return super().model_validate({"testcases": []})
        
        # 리스트인 경우 직접 testcases로 매핑
        if isinstance(obj, list):
            return super().model_validate({"testcases": obj})
        
        # 기본값 반환
        return super().model_validate({"testcases": []})
    
class TestCaseRequest(BaseModel):
    test_case_id: str
    testcases: List[Dict[str, str]]