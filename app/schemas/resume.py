from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

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
class CommitFile(BaseModel):
    repository: str
    commitFiles: List[str]

class PortfolioRequest(BaseModel):
    repositories: List[str]
    commitFiles: List[CommitFile]

# 기능 설명 스키마
class FeatureDetail(BaseModel):
    description: List[str] = Field(description="기능에 대한 상세 설명 목록")

# 아키텍처 컴포넌트 스키마
class ServiceComponent(BaseModel):
    name: str = Field(description="서비스 이름")
    port: Optional[int] = Field(description="서비스 포트", default=None)
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
    architecture: Optional[SystemArchitecture] = Field(description="시스템 아키텍처 상세 정보", default=None)

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
                    "tech_stack": ["Spring Boot", "Java 11", "PostgreSQL", "PostGIS", "Kafka", "Redis", "Docker", "Kubernetes"],
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

class PortfolioRole(BaseModel):
    """개발자의 프로젝트 역할과 기여도 정보"""
    roles: List[str] = Field(description="주요 역할 및 성과 목록 (예: 'MSA를 사용해서 서버 구축하여 10개의 서비스 연결 및 안정적인 운영')")

    class Config:
        schema_extra = {
            "example": {
                "roles": [
                    "Terraform을 사용해서 클라우드 인프라 프로비저닝 자동화하여 배포 시간 80% 단축",
                    "GitAction을 사용해서 무중단 배포 파이프라인 구축하여 서비스 다운타임 제로 달성",
                    "API Gateway를 사용해서 서비스 간 연결 아키텍처 설계하여 API 평균 응답시간 58ms 단축",
                    "AI 기술을 사용해서 강아지 얼굴 판별 및 유사도 비교 서버 구축하여 이미지 처리 시간 10초 단축",
                    "MSA 아키텍처를 사용해서 서비스 설계 및 구현하여 시스템 확장성 200% 향상",
                    "클라우드 기술을 사용해서 인프라 자동화하여 운영 비용 40% 절감",
                    "CI/CD 도구를 사용해서 배포 파이프라인 구축하여 배포 시간 90% 단축",
                    "Kafka, RestAPI을 사용해서 서비스 연동 구현하여 10개의 서비스 안정적 운영"
                ]
            }
        }

class Project(BaseModel):
    """프로젝트 정보"""
    name: str = Field(description="프로젝트 이름")
    techStack: List[str] = Field(description="사용된 기술 스택", default_factory=list)
    role: List[str] = Field(description="프로젝트에서의 역할")

class Career(BaseModel):
    """경력 정보"""
    position: str = Field(description="직무/포지션")
    achievement: str = Field(description="주요 성과")

class ResumeSummaryRequest(BaseModel):
    """이력서 요약 요청 스키마"""
    position: str = Field(description="지원 포지션")
    projects: List[Project] = Field(description="프로젝트 목록", default_factory=list)
    careers: List[Career] = Field(description="경력 목록", default_factory=list)

class ResumeSummary(BaseModel):
    """이력서 요약 응답 스키마"""
    techStack: List[str] = Field(description="추천 기술 스택 목록")
    techSummary: List[str] = Field(description="기술 스택 요약 설명")

    class Config:
        schema_extra = {
            "example": {
                "techStack": ["Spring Boot", "PostgreSQL", "Kafka", "Meilisearch", "WebSocket", "AWS S3", "Docker"],
                "techSummary": [
                    "Terraform을 사용해서 클라우드 인프라 프로비저닝 자동화하여 배포 시간 80% 단축",
                    "GitAction을 사용해서 무중단 배포 파이프라인 구축하여 서비스 다운타임 제로 달성",
                    "API Gateway를 사용해서 서비스 간 연결 아키텍처 설계하여 API 평균 응답시간 58ms 단축",
                    "AI 기술을 사용해서 강아지 얼굴 판별 및 유사도 비교 서버 구축하여 이미지 처리 시간 10초 단축",
                    "MSA 아키텍처를 사용해서 서비스 설계 및 구현하여 시스템 확장성 200% 향상",
                    "클라우드 기술을 사용해서 인프라 자동화하여 운영 비용 40% 절감",
                    "CI/CD 도구를 사용해서 배포 파이프라인 구축하여 배포 시간 90% 단축",
                    "Kafka, RestAPI을 사용해서 서비스 연동 구현하여 10개의 서비스 안정적 운영"
                ]
            }
        }

class JobDescriptionRequest(BaseModel):
    url: str = Field(description="채용 공고 URL")

# JobAnalysis 스키마도 실제 데이터에 맞게 수정
class JobAnalysis(BaseModel):
    company: str = Field(description="회사명")
    position: str = Field(description="직무/포지션")
    mainTasks: List[str] = Field(description="주요 업무 목록")
    requirements: List[str] = Field(description="자격 요건 및 우대 사항 목록")
    career: str = Field(description="경력 요구사항")
    resumeRequirements: List[str] = Field(description="이력서 요구사항 목록")
    recruitmentProcess: List[str] = Field(description="채용 절차 목록")
    # additionalInfo를 선택적으로 변경 (프론트에서 항상 보내지 않을 수 있음)
    additionalInfo: Optional[List[str]] = Field(description="추가 정보 목록", default_factory=list)

class AiAnalysisResponse(BaseModel):
    analysis: JobAnalysis

class Author(BaseModel):
    id: int
    nickname: str

class Link(BaseModel):
    type: str
    url: str

class ResumeCareer(BaseModel):
    company: str
    position: str
    isCurrent: bool
    startDate: str
    endDate: Optional[str] = None
    description: str
    achievement: str
    # 선택적 필드
    period: Optional[str] = None

class ResumeProject(BaseModel):
    name: str
    description: str
    techStack: List[str]
    role: str
    startDate: date
    endDate: Optional[date] = None
    memberCount: Optional[int] = None
    memberRoles: Optional[str] = None
    githubLink: Optional[str] = None
    deployLink: Optional[str] = None

class Education(BaseModel):
    school: str
    major: str
    startDate: date
    endDate: Optional[date] = None
    degree: str
    note: Optional[str] = None

class Certificate(BaseModel):
    type: str
    name: str
    date: date
    organization: str

class CoverLetter(BaseModel):
    title: str
    content: str

class PortfolioDuration(BaseModel):
    startDate: str
    endDate: str

class PortfolioArchitecture(BaseModel):
    communication: str
    deployment: str

class PortfolioContents(BaseModel):
    techStack: str
    summary: str
    description: str
    roles: Optional[List[str]] = None
    features: Dict[str, List[str]]
    architecture: PortfolioArchitecture

class GitHubRepo(BaseModel):
    name: str
    url: str
    description: str
    language: str
    lineCount: int
    byteSize: int
    selectedDirectories: List[str]

class SavedFile(BaseModel):
    id: str
    name: str
    path: str
    repository: str
    savedPath: str

class ResumePortfolio(BaseModel):
    id: str
    spaceId: int
    title: str
    author: Author
    duration: PortfolioDuration
    githubLink: Optional[str] = None
    deployLink: Optional[str] = None
    memberCount: Optional[int] = None
    memberRoles: Optional[str] = None
    contents: PortfolioContents
    # 선택적 필드들 - 프론트에서 보내지 않을 수 있음
    thumbnailUrl: Optional[str] = None
    githubRepos: Optional[List[Any]] = None
    savedFiles: Optional[List[Any]] = None
    createdAt: Optional[str] = None  # datetime -> str로 변경 (프론트에서 문자열로 보냄)
    updatedAt: Optional[str] = None  # datetime -> str로 변경

    class Config:
        from_attributes = True

# CustomResumeRequest 스키마 수정
class CustomResumeRequest(BaseModel):
    jobDescription: Optional[JobAnalysis] = None
    selectedPortfolios: Optional[List[ResumePortfolio]] = None
    careers: Optional[List[ResumeCareer]] = None
    additionalInfo: Optional[List[str]] = Field(default_factory=list)

    class Config:
        # 추가 필드 허용 (향후 확장성을 위해)
        extra = "ignore"

class CoverLetterSection(BaseModel):
    title: str
    content: str

class TechStackAnalysis(BaseModel):
    tech_stack: List[str]
    tech_capabilities: List[str]

class CustomResumeResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    message: str

    