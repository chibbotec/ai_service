from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ContestBase(BaseModel):
    title: str
    space_id: int
    timeout_millis: int
    submit: int = 0

class ContestCreate(ContestBase):
    pass

class ContestResponse(ContestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProblemBase(BaseModel):
    contest_id: int
    tech_interview_id: int

class ProblemCreate(ProblemBase):
    pass

class ProblemResponse(ProblemBase):
    id: int

    class Config:
        from_attributes = True

class ParticipantBase(BaseModel):
    member_id: int
    nickname: str
    contest_id: int
    submit: int = 0

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantResponse(ParticipantBase):
    id: int

    class Config:
        from_attributes = True

class AnswerBase(BaseModel):
    answer: str
    feedback: Optional[str] = None
    rank_score: int
    participant_id: int
    problem_id: int

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: int

    class Config:
        from_attributes = True

# 테스트 케이스 관련 스키마
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