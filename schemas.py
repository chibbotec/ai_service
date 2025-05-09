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

class ParticipantAnswer(BaseModel):
    participant_id: int
    nickname: str
    answer: str
    rank_score: int = 0

class Problem(BaseModel):
    id: int
    problem: str
    ai_answer: str
    answers: List[ParticipantAnswer]

class Contest(BaseModel):
    id: int
    title: str
    problems: List[Problem]

# AI 테스트 케이스 생성 입력 스키마
class Evaluation(BaseModel):
    """AI 답변 평가를 위한 스키마"""
    score: int = Field(description="답변의 점수 (0-100)")
    feedback: str = Field(description="답변에 대한 피드백")

    class Config:
        schema_extra = {
            "example": {
                "score": 100,
                "feedback": "응시자는 동기와 비동기 통신의 기본 개념을 이해하고 있는 것으로 보입니다..."
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

# 기능 설명 스키마
class FeatureDetail(BaseModel):
    description: List[str] = Field(description="기능에 대한 상세 설명 목록")

# 아키텍처 컴포넌트 스키마
class ServiceComponent(BaseModel):
    name: str = Field(description="서비스 이름")
    port: int = Field(description="서비스 포트")
    description: str = Field(description="서비스 설명")
    functions: List[str] = Field(description="주요 기능 목록")

# 아키텍처 스키마
class SystemArchitecture(BaseModel):
    overview: str = Field(description="시스템 아키텍처 개요")
    components: List[ServiceComponent] = Field(description="시스템 구성 컴포넌트")
    tech_stack: Dict[str, List[str]] = Field(description="기술 스택 분류")
    communication: str = Field(description="서비스 간 통신 방식")
    deployment: str = Field(description="배포 구조")

# 포트폴리오 데이터 스키마
class PortfolioData(BaseModel):
    """포트폴리오 데이터 스키마"""
    summary: str = Field(description="프로젝트 요약 (최대 100단어)")
    overview: str = Field(description="프로젝트 개요 (최대 300단어)")
    tech_stack: List[str] = Field(description="사용된 기술 스택")
    features: Dict[str, List[str]] = Field(description="주요 기능 및 설명")
    architecture: SystemArchitecture = Field(description="시스템 아키텍처 상세 정보")

    class Config:
        schema_extra = {
            "example": {
                "summary": "이 프로젝트는 실종된 반려동물을 찾는 과정을 돕기 위한 통합 플랫폼입니다.",
                "overview": "여기에서 Paw는 반려동물의 발자국을 의미하며, 길을 잃은 반려동물이 집으로 돌아오는 발자국을 따라갈 수 있도록 도와주는 서비스입니다. AI 얼굴 인식, 위치 기반 검색, 실시간 알림 등 다양한 기능을 통해 실종 반려동물과 발견 반려동물을 매칭하고, 사용자 간 소통을 지원합니다.",
                "tech_stack": ["Spring Boot", "PostgreSQL", "Kafka", "Meilisearch", "WebSocket", "AWS S3", "Docker"],
                "features": {
                    "회원 관리": [
                        "일반 로그인 및 카카오 소셜 로그인 지원",
                        "사용자 프로필 관리 기능",
                        "반려동물 등록 및 정보 관리 기능"
                    ],
                    "실종/발견 게시글": [
                        "실종 동물 신고 등록 및 관리",
                        "발견 동물 신고 등록 및 관리",
                        "반경 기반 위치 검색 기능",
                        "다중 이미지 업로드 지원"
                    ],
                    "AI 얼굴 인식": [
                        "동물 얼굴 인식을 통한 유사 게시글 매칭",
                        "비동기 처리를 통한 성능 최적화",
                        "매칭 결과 실시간 알림 제공"
                    ]
                },
                "architecture": {
                    "overview": "마이크로서비스 아키텍처를 기반으로 구성된 확장 가능한 시스템으로, 각 서비스는 독립적으로 배포 가능합니다.",
                    "components": [
                        {
                            "name": "API Gateway",
                            "port": 8001,
                            "description": "모든 요청의 진입점 역할",
                            "functions": ["JWT 인증", "요청 라우팅", "로드 밸런싱"]
                        },
                        {
                            "name": "회원 서비스",
                            "port": 8090,
                            "description": "사용자 및 반려동물 정보 관리",
                            "functions": ["회원 등록/수정/삭제", "OAuth2 인증", "반려동물 프로필 관리"]
                        }
                    ],
                    "tech_stack": {
                        "백엔드": ["Spring Boot", "Java 11"],
                        "데이터베이스": ["PostgreSQL", "PostGIS"],
                        "메시징": ["Kafka", "Redis"],
                        "배포": ["Docker", "Kubernetes"]
                    },
                    "communication": "API Gateway를 통한 HTTP 라우팅과 Kafka를 활용한 비동기 이벤트 기반 통신을 결합하여 사용합니다.",
                    "deployment": "모든 서비스는 Docker 컨테이너화되어 Kubernetes 클러스터에서 관리됩니다."
                }
            }
        }

class PortfolioResponse(BaseModel):
    summary: str
    overview: str
    features: list[str]
    architecture: str