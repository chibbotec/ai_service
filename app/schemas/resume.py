from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ResumeBase(BaseModel):
    content: str
    member_id: int

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# 포트폴리오 요청 스키마
class PortfolioRequest(BaseModel):
    repositories: List[str]

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