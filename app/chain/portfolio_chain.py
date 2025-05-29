from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume import PortfolioData

# 출력 파서 생성
parser = PydanticOutputParser(pydantic_object=PortfolioData)

# 프롬프트 템플릿 생성
template = """
당신은 IT채용 전문가입니다. 주어진 소스 코드를 분석하여 이력서에 포함할 포트폴리오 내용을 생성해 주세요.

{format_instructions}

다음 소스 코드를 기반으로 프로젝트 포트폴리오를 작성해 주세요:

{source_code}

다음 지침을 따라 포트폴리오를 작성해 주세요:
1. 프로젝트 요약은 간결하고 명확하게 작성해 주세요 (최대 100단어).
2. 프로젝트 개요에는 목적과 문제 해결 방식을 자세히 설명해 주세요 (최대 300단어).
3. 사용된 기술 스택을 모두 리스트로 나열해 주세요.
   예시: ["Spring Boot", "PostgreSQL", "Kafka", "Meilisearch", "WebSocket", "AWS S3", "Docker"]
   주의: 기술 스택은 반드시 문자열 리스트 형태여야 합니다.
4. 주요 기능은 도메인별로 그룹화하여 작성하고, 각 기능에 대한 자세한 설명을 포함해주세요.
   예시 형식: {{"기능명": ["설명1", "설명2", ...]}}
   주의: 각 기능의 설명은 반드시 문자열 리스트 형태여야 합니다.
5. 시스템 아키텍처는 다음 구성요소를 포함해 주세요:
   - overview: 전체 아키텍처 개요
   - components: 각 서비스 구성요소와 포트, 설명, 주요 기능
   - communication: 서비스 간 통신 방식
   - deployment: 배포 구성 방식

예시 응답:
{{
    "summary": "이 프로젝트는 실종된 반려동물을 찾는 과정을 돕기 위한 통합 플랫폼입니다.",
    "overview": "여기에서 Paw는 반려동물의 발자국을 의미하며, 길을 잃은 반려동물이 집으로 돌아오는 발자국을 따라갈 수 있도록 도와주는 서비스입니다. AI 얼굴 인식, 위치 기반 검색, 실시간 알림 등 다양한 기능을 통해 실종 반려동물과 발견 반려동물을 매칭하고, 사용자 간 소통을 지원합니다.",
    "tech_stack": ["Spring Boot", "PostgreSQL", "Kafka", "Meilisearch", "WebSocket", "AWS S3", "Docker"],
    "features": {{
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
    }},
    "architecture": {{
        "overview": "마이크로서비스 아키텍처를 기반으로 구성된 확장 가능한 시스템으로, 각 서비스는 독립적으로 배포 가능합니다.",
        "components": [
            {{
                "name": "API Gateway",
                "port": "8001",
                "description": "모든 요청의 진입점 역할",
                "functions": ["JWT 인증", "요청 라우팅", "로드 밸런싱"]
            }},
            {{
                "name": "회원 서비스",
                "port": "8090",
                "description": "사용자 및 반려동물 정보 관리",
                "functions": ["회원 등록/수정/삭제", "OAuth2 인증", "반려동물 프로필 관리"]
            }},
            {{
                "name": "크롤러 서비스",
                "port": "별도",
                "description": "외부 데이터 수집 및 분석",
                "functions": ["웹 크롤링", "데이터 정제", "분석 결과 저장"]
            }}
        ],
        "communication": "API Gateway를 통한 HTTP 라우팅과 Kafka를 활용한 비동기 이벤트 기반 통신을 결합하여 사용합니다.",
        "deployment": "모든 서비스는 Docker 컨테이너화되어 Kubernetes 클러스터에서 관리됩니다."
    }}
}}
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["source_code"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(
    temperature=0.3, 
    model_name="gpt-4.1-nano",  # 더 큰 컨텍스트를 지원하는 모델로 변경
    max_tokens=32768,  # 출력 토큰 수 제한
    request_timeout=300  # 타임아웃 시간 증가
)

# 체인 구성
chain = prompt | llm | parser
