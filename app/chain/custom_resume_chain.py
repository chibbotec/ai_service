from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.utils.progress_tracker import ProgressTracker
from app.utils.progress_tracker import ProgressStatus
from app.schemas.resume import CustomResumeRequest, JobAnalysis
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from app.chain.portfolio_chain import chain as portfolio_chain
from app.chain.portfolio_role_chain import role_chain
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from datetime import datetime, timedelta
from langchain.schema.runnable import RunnablePassthrough
import asyncio
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class MemoryManager:
    """사용자 메모리 관리 클래스"""
    def __init__(self):
        self.memories: Dict[str, ConversationBufferMemory] = {}
        self.last_access: Dict[str, datetime] = {}
    
    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """사용자별 메모리 인스턴스를 가져오거나 생성"""
        if user_id not in self.memories:
            self.memories[user_id] = ConversationBufferMemory()
        
        self.last_access[user_id] = datetime.now()
        return self.memories[user_id]
    
    def clear_memory(self, user_id: str) -> None:
        """특정 사용자의 메모리 초기화"""
        if user_id in self.memories:
            del self.memories[user_id]
        if user_id in self.last_access:
            del self.last_access[user_id]
    
    async def cleanup_old_memories(self, max_age_hours: int = 24) -> None:
        """오래된 메모리 정리"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_users = [
            user_id for user_id, last_time in self.last_access.items()
            if last_time < cutoff_time
        ]
        for user_id in expired_users:
            self.clear_memory(user_id)
        
        if expired_users:
            logger.info(f"Cleaned up memory for {len(expired_users)} users")

# 전역 메모리 매니저 인스턴스
memory_manager = MemoryManager()

class PortfolioAnalysis(BaseModel):
    """포트폴리오 분석 결과"""
    name: str = Field(description="프로젝트명")
    description: str = Field(description="프로젝트 소개")
    techStack: List[str] = Field(description="기술 스택")
    role: List[str] = Field(description="주요 역할 및 성과")
    startDate: str = Field(description="시작일 (YYYY-MM-DD)")
    endDate: str = Field(description="종료일 (YYYY-MM-DD)")
    memberCount: int = Field(description="참여 인원 수")
    memberRoles: str = Field(description="프로젝트 내 역할 (PO, PM, Fullstack, Backend, Frontend, Publisher)")
    githubLink: Optional[str] = Field(description="GitHub 링크", default=None)
    deployLink: Optional[str] = Field(description="배포 링크", default=None)

class ProjectAnalysis(BaseModel):
    """프로젝트 분석 결과"""
    projects: List[PortfolioAnalysis] = Field(description="분석된 프로젝트 목록")

class ProjectResponse(BaseModel):
    """프로젝트 분석 응답"""
    status: str = Field(description="응답 상태")
    result: ProjectAnalysis = Field(description="분석 결과")
    message: str = Field(description="응답 메시지")

class TotalPortfolioAnalysis(BaseModel):
    """포트폴리오 분석 결과"""
    portfolios: List[PortfolioAnalysis] = Field(description="포트폴리오 분석 결과")

class CareerAnalysis(BaseModel):
    """경력 분석 결과"""
    company: str = Field(description="회사명")
    position: str = Field(description="직급")
    isCurrent: bool = Field(description="현재 재직 중 여부")
    startDate: str = Field(description="입사일 (YYYY-MM-DD)")
    endDate: Optional[str] = Field(description="퇴사일 (YYYY-MM-DD)", default=None)
    description: str = Field(description="직무 내용")
    achievement: str = Field(description="주요 성과")

class CareerResponse(BaseModel):
    """경력 분석 응답"""
    status: str = Field(description="응답 상태")
    result: List[CareerAnalysis] = Field(description="분석된 경력 목록")
    message: str = Field(description="응답 메시지")

class TotalCareerAnalysis(BaseModel):
    """전체 경력 분석 결과"""
    careers: List[CareerAnalysis] = Field(description="분석된 경력 목록")

class TechStackAnalysis(BaseModel):
    """기술 스택 분석 결과"""
    tech_stack: List[str] = Field(description="지원자의 주요 기술 스택 목록")
    tech_summary: List[str] = Field(description="지원자의 주요 기술 역량 요약")

class CoverLetterSection(BaseModel):
    """자기소개서 섹션"""
    title: str = Field(description="섹션 제목")
    content: str = Field(description="섹션 내용")

class CoverLetter(BaseModel):
    """자기소개서 내용"""
    coverLetter: List[CoverLetterSection] = Field(description="자기소개서 섹션 목록")

def validate_processed_data(processed_data: Dict[str, Any], required_keys: List[str]) -> None:
    """입력 데이터 검증"""
    for key in required_keys:
        if key not in processed_data:
            raise ValueError(f"Missing required field: {key}")
        if not processed_data[key] or (isinstance(processed_data[key], str) and not processed_data[key].strip()):
            raise ValueError(f"Empty value for required field: {key}")

async def generate_start(processed_data: Dict[str, Any], tracker: ProgressTracker, user_id: str) -> str:
    """
    시작하기 체인 - 채용 담당자와의 대화 시작
    """
    try:
        # 입력 데이터 검증
        validate_processed_data(processed_data, ["job_description"])
        
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")
        memory = memory_manager.get_memory(user_id)
        
        prompt = PromptTemplate(
            input_variables=["job_description", "history"],
            template="""당신은 {job_description}의 채용 담당자입니다.
지원자와의 대화를 시작하세요. 지원자의 이력서와 포트폴리오를 검토하고 있다는 것을 언급하세요.

이전 대화 내용:
{history}"""
        )
        
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=True
        )
        
        result = await chain.ainvoke({
            "job_description": processed_data["job_description"]
        })
        
        response = result.get("text", "")
        progress = tracker.get_progress()
        completed_steps = progress.get("completed_steps", [])
        completed_steps.append("start")
        await tracker.update(
            status=ProgressStatus.SUCCESS, 
            metadata={
                "current_step": "start",
                "completed_steps": completed_steps
            }
        )
        return response
        
    except Exception as e:
        logger.error(f"Error in generate_start: {str(e)}")
        await tracker.update(
            status=ProgressStatus.ERROR, 
            metadata={"current_step": "start", "error": str(e)}
        )
        raise

async def generate_portfolio(processed_data: Dict[str, Any], tracker: ProgressTracker, user_id: str) -> TotalPortfolioAnalysis:
    try:
        validate_processed_data(processed_data, ["portfolio_info", "job_description"])
        
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")
        memory = memory_manager.get_memory(user_id)
        parser = PydanticOutputParser(pydantic_object=TotalPortfolioAnalysis)

        # 메모리에서 이전 대화 내용 가져오기
        chat_history = ""
        if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
            messages = memory.chat_memory.messages
            if messages:
                history_parts = []
                for msg in messages[-6:]:  # 최근 6개 메시지
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        msg_type = "Human" if msg.type == "human" else "AI"
                        history_parts.append(f"{msg_type}: {msg.content}")
                chat_history = "\n".join(history_parts)

        prompt = PromptTemplate.from_template("""당신은 {job_description}의 채용 담당자입니다.
지원자의 이력서와 포트폴리오를 검토한 결과를 바탕으로, 포트폴리오를 분석해주세요.                                            
각 포트폴리오 별로 채용 담당자가 중요하게 생각하는 기술 스택과 한국말로 역량을 정리해주세요. 
각 포트폴리오 별로 채용 담당자가 중요하게 생각 하는 순으로 내림 차순으로 만들어 주세요.  

포트폴리오 정보:
{portfolio_info}
                                              
이전 대화 내용:
{history}

{format_instructions}
                                              
1. 프로젝트명은 그대로 사용합니다.
2. 프로젝트 소개는 그대로 사용합니다.
3. 기술스택은 채용담당자가 중요하게 생각하는 순으로 정리합니다.
4. 주요 역할 및 성과는 채용담당자가 중요하게 생각하는 순으로 작성하고 아래의 형식과 같이 작성합니다.
    - 기존의 주요 역할 및 성과를 포함해서 작성합니다.
    - 각 항목은 반드시 "{{기술}}을 사용해서 {{기능}} 구현 {{성과}}" 형식으로 작성해 주세요.
    - 성과는 구체적인 수치나 개선 효과를 포함해야 합니다.
    - 예시: "Terraform을 사용해서 클라우드 인프라 프로비저닝 자동화하여 배포 시간 80% 단축"
    - 예시: "GitAction을 사용해서 무중단 배포 파이프라인 구축하여 서비스 다운타임
5. 시작일은 yy.mm.dd를 YYYY-MM-DD으로 변환해서 사용합니다.
6. 종료일은 yy.mm.dd를 YYYY-MM-DD으로 변환해서 사용합니다.
7. 참여 인원 수는 그대로 사용합니다.
8. 프로젝트 내 역할은 그대로 사용합니다.
9. GitHub 링크는 있으면 그대로 사용합니다. 없으면 ""으로 표시해주세요
10. 배포 링크는 있으면 그대로 사용합니다. 없으면 ""으로 표시해주세요

응답은 반드시 다음 형식을 따라야 합니다:
{{
    "portfolios": [
        {{
            "name": "프로젝트명",
            "description": "프로젝트 소개",
            "techStack": ["기술1", "기술2", "기술3"],
            "role": ["주요 역할 및 성과1", "주요 역할 및 성과2", "주요 역할 및 성과3"],
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD",
            "memberCount": 5,
            "memberRoles": "프로젝트 내 역할",
            "githubLink": "GitHub 링크 또는 빈 문자열",
            "deployLink": "배포 링크 또는 빈 문자열"
        }}
    ]
}}""")
        
        # 체인 구성
        chain = (
            {
                "job_description": lambda x: x["job_description"],
                "portfolio_info": lambda x: x["portfolio_info"],
                "history": lambda x: x["history"],
                "format_instructions": lambda x: parser.get_format_instructions()
            }
            | prompt
            | llm
            | parser
        )

                # 데이터 준비
        input_data = {
            "job_description": processed_data["job_description"],
            "portfolio_info": processed_data["portfolio_info"],
            "history": chat_history or "이전 대화가 없습니다."
        }
        
        # 실행
        parsed_response = await chain.ainvoke(input_data)

        # 메모리에 대화 저장
        user_message = "포트폴리오들 분석 및 정리해주세요"
        ai_response = str(parsed_response)
        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(ai_response)
        
        progress = tracker.get_progress()
        completed_steps = progress.get("completed_steps", [])
        completed_steps.append("portfolio")
        await tracker.update(
            status=ProgressStatus.SUCCESS, 
            metadata={
                "current_step": "portfolio",
                "completed_steps": completed_steps,
                "message": "포트폴리오 분석이 완료되었습니다."
            }
        )
        return parsed_response
        
    except Exception as e:
        logger.error(f"Error in generate_portfolio: {str(e)}")
        await tracker.update(
            status=ProgressStatus.ERROR, 
            metadata={"current_step": "portfolio", "error": str(e)}
        )
        raise

async def generate_career(processed_data: Dict[str, Any], tracker: ProgressTracker, user_id: str) -> TotalCareerAnalysis:
    try:
        validate_processed_data(processed_data, ["career_info", "job_description"])
        
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")
        memory = memory_manager.get_memory(user_id)
        parser = PydanticOutputParser(pydantic_object=TotalCareerAnalysis)

        # 메모리에서 이전 대화 내용 가져오기
        chat_history = ""
        if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
            messages = memory.chat_memory.messages
            if messages:
                history_parts = []
                for msg in messages[-6:]:  # 최근 6개 메시지
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        msg_type = "Human" if msg.type == "human" else "AI"
                        history_parts.append(f"{msg_type}: {msg.content}")
                chat_history = "\n".join(history_parts)

        prompt = PromptTemplate.from_template("""당신은 {job_description}의 채용 담당자입니다.
지원자의 이력서와 경력을 검토한 결과를 바탕으로, 경력을 분석해주세요.                                            
각 경력 별로 채용 담당자가 중요하게 생각하는 직무 내용과 성과를 정리해주세요. 
각 경력 별로 채용 담당자가 중요하게 생각 하는 순으로 내림 차순으로 만들어 주세요.  

경력 정보:
{career_info}
                                              
이전 대화 내용:
{history}

{format_instructions}
                                              
1. 회사명은 그대로 사용합니다.
2. 직급은 그대로 사용합니다.
3. 현재 재직 중 여부는 그대로 사용합니다.
4. 입사일은 그대로 사용합니다.
5. 퇴사일은 있으면 그대로 사용하고, 현재 재직 중이면 null로 표시합니다.
6. 직무 내용은 채용담당자가 중요하게 생각하는 순으로 정리합니다.
7. 주요 성과는 채용담당자가 중요하게 생각하는 순으로 정리합니다.

응답은 반드시 다음 형식을 따라야 합니다:
{{
    "careers": [
        {{
            "company": "회사명",
            "position": "직급",
            "isCurrent": true/false,
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD 또는 null",
            "description": "직무 내용",
            "achievement": "주요 성과"
        }}
    ]
}}""")
        
        # 체인 구성
        chain = (
            {
                "job_description": lambda x: x["job_description"],
                "career_info": lambda x: x["career_info"],
                "history": lambda x: x["history"],
                "format_instructions": lambda x: parser.get_format_instructions()
            }
            | prompt
            | llm
            | parser
        )

        # 데이터 준비
        input_data = {
            "job_description": processed_data["job_description"],
            "career_info": processed_data["career_info"],
            "history": chat_history or "이전 대화가 없습니다."
        }
        
        # 실행
        parsed_response = await chain.ainvoke(input_data)

        # 메모리에 대화 저장
        user_message = "경력사항 분석 및 정리해주세요"
        ai_response = str(parsed_response)
        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(ai_response)
        
        progress = tracker.get_progress()
        completed_steps = progress.get("completed_steps", [])
        completed_steps.append("career")
        await tracker.update(
            status=ProgressStatus.SUCCESS, 
            metadata={
                "current_step": "career",
                "completed_steps": completed_steps,
                "message": "경력 분석이 완료되었습니다."
            }
        )
        return parsed_response
        
    except Exception as e:
        logger.error(f"Error in generate_career: {str(e)}")
        await tracker.update(
            status=ProgressStatus.ERROR, 
            metadata={"current_step": "career", "error": str(e)}
        )
        raise

async def generate_tech_stack(processed_data: Dict[str, Any], tracker: ProgressTracker, user_id: str) -> TechStackAnalysis:
    try:
        validate_processed_data(processed_data, ["job_description"])
        
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")
        memory = memory_manager.get_memory(user_id)
        parser = PydanticOutputParser(pydantic_object=TechStackAnalysis)
        
        # 메모리에서 이전 대화 내용 가져오기
        chat_history = ""
        if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
            messages = memory.chat_memory.messages
            if messages:
                history_parts = []
                for msg in messages[-6:]:  # 최근 6개 메시지
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        msg_type = "Human" if msg.type == "human" else "AI"
                        history_parts.append(f"{msg_type}: {msg.content}")
                chat_history = "\n".join(history_parts)
        
        # 포트폴리오와 경력 정보가 없는 경우 처리
        portfolio_info = processed_data.get("portfolio_info", "")
        career_info = processed_data.get("career_info", "")
        
        prompt = PromptTemplate.from_template("""당신은 {job_description}의 채용 담당자입니다.
지원자의 포트폴리오와 경력을 검토한 결과를 바탕으로, 
채용 담당자가 중요하게 생각하는 기술 스택과 한국말로 역량을 정리해주세요. 
채용 담당자가 중요하게 생각 하는 순으로 내림 차순으로 만들어 주세요.

포트폴리오 정보:
{portfolio_info}

경력 정보:
{career_info}

이전 대화 내용:
{history}

{format_instructions}

1. 기술 스택은 채용담당자가 중요하게 생각하는 순으로 정리합니다.
2. 기술 역량 요약은 채용담당자가 중요하게 생각하는 순으로 정리합니다.
3. 포트폴리오나 경력 정보가 없는 경우에도 채용 공고를 바탕으로 분석해주세요.

응답은 반드시 다음 형식을 따라야 합니다:
{{
    "tech_stack": ["기술1", "기술2", "기술3"],
    "tech_summary": ["역량1", "역량2", "역량3"]
}}""")
        
        # 체인 구성
        chain = (
            {
                "job_description": lambda x: x["job_description"],
                "portfolio_info": lambda x: x.get("portfolio_info", ""),
                "career_info": lambda x: x.get("career_info", ""),
                "history": lambda x: x["history"],
                "format_instructions": lambda x: parser.get_format_instructions()
            }
            | prompt
            | llm
            | parser
        )
        
        # 데이터 준비
        input_data = {
            "job_description": processed_data["job_description"],
            "portfolio_info": portfolio_info,
            "career_info": career_info,
            "history": chat_history or "이전 대화가 없습니다."
        }
        
        # 실행
        parsed_response = await chain.ainvoke(input_data)

        # 메모리에 대화 저장
        user_message = "기술 스택 분석 및 정리해주세요"
        ai_response = str(parsed_response)
        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(ai_response)
        
        progress = tracker.get_progress()
        completed_steps = progress.get("completed_steps", [])
        completed_steps.append("tech_stack")
        await tracker.update(
            status=ProgressStatus.SUCCESS, 
            metadata={
                "current_step": "tech_stack",
                "completed_steps": completed_steps,
                "message": "기술 스택 분석이 완료되었습니다."
            }
        )
        return parsed_response
        
    except Exception as e:
        logger.error(f"Error in generate_tech_stack: {str(e)}")
        await tracker.update(
            status=ProgressStatus.ERROR, 
            metadata={"current_step": "tech_stack", "error": str(e)}
        )
        raise

async def generate_coverletter(processed_data: Dict[str, Any], tracker: ProgressTracker, user_id: str) -> CoverLetter:
    """
    자기소개서 생성 체인 - 이전 대화 내용과 추가 정보를 바탕으로 자기소개서 생성
    """
    try:
        # 입력 데이터 검증
        validate_processed_data(processed_data, ["job_description", "additional_info"])
        
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4.1")
        memory = memory_manager.get_memory(user_id)
        parser = PydanticOutputParser(pydantic_object=CoverLetter)
        
        # 메모리에서 이전 대화 내용 가져오기
        chat_history = ""
        if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
            messages = memory.chat_memory.messages
            if messages:
                history_parts = []
                for msg in messages[-6:]:  # 최근 6개 메시지
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        msg_type = "Human" if msg.type == "human" else "AI"
                        history_parts.append(f"{msg_type}: {msg.content}")
                chat_history = "\n".join(history_parts)
        
        prompt = PromptTemplate.from_template("""당신은 {job_description}의 채용 담당자입니다.
이전 대화 내용을 기억하면서, {job_description}의 이력서 요구사항과 지원자의 추가 정보를 종합하여
자기소개서를 작성해주세요. 이전 대화에서 언급된 지원자의 강점과 경험을 최대한 활용하세요.

추가 정보:
{additional_info}

이전 대화 내용:
{history}

{format_instructions}

다음 가이드라인에 따라 자기소개서를 작성해주세요:

1. 각 섹션은 반드시 title과 content를 포함해야 합니다.
2. title은 간단명료하게 작성하고, content는 구체적이고 상세하게 작성해주세요.
3. 이전 대화에서 언급된 지원자의 강점과 프로젝트 경험을 최대한 활용하세요.
4. 채용 공고의 요구사항과 지원자의 경험을 연결하여 작성하세요.
5. 각 섹션은 서로 연결성이 있어야 하며, 전체적인 스토리가 자연스럽게 이어져야 합니다.
6. 구체적인 예시와 수치를 포함하여 작성하세요.
7. 회사와 직무에 대한 이해도를 보여주세요.
8. 지원자의 열정과 성장 가능성을 보여주세요.

응답은 반드시 다음 형식을 따라야 합니다:
{{
    "coverLetter": [
        {{
            "title": "섹션 제목",
            "content": "섹션 내용"
        }},
        ...
    ]
}}""")
        
        # 체인 구성 (generate_tech_stack과 동일한 방식)
        chain = (
            {
                "job_description": lambda x: x["job_description"],
                "additional_info": lambda x: x["additional_info"],
                "history": lambda x: x["history"],
                "format_instructions": lambda x: parser.get_format_instructions()
            }
            | prompt
            | llm
            | parser
        )
        
        # 데이터 준비
        input_data = {
            "job_description": processed_data["job_description"],
            "additional_info": processed_data["additional_info"],
            "history": chat_history or "이전 대화가 없습니다."
        }
        
        # 실행
        parsed_response = await chain.ainvoke(input_data)
        
        # 메모리에 대화 저장
        user_message = "자기소개서를 작성해주세요."
        ai_response = str(parsed_response)
        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(ai_response)
        
        progress = tracker.get_progress()
        completed_steps = progress.get("completed_steps", [])
        completed_steps.append("cover_letter")
        await tracker.update(
            status=ProgressStatus.SUCCESS, 
            metadata={
                "current_step": "cover_letter",
                "completed_steps": completed_steps,
                "message": "자기소개서 생성이 완료되었습니다."
            }
        )
        return parsed_response
        
    except Exception as e:
        logger.error(f"Error in generate_coverletter: {str(e)}")
        await tracker.update(
            status=ProgressStatus.ERROR, 
            metadata={"current_step": "cover_letter", "error": str(e)}
        )
        # 파싱 실패 시 기본값 반환
        return CoverLetter(
            coverLetter=[
                CoverLetterSection(
                    title="자기소개서 생성 오류",
                    content="자기소개서 생성 중 오류가 발생했습니다. 다시 시도해 주세요."
                )
            ]
        )

def clear_user_memory(user_id: str) -> None:
    """
    사용자의 대화 메모리를 초기화합니다.
    """
    memory_manager.clear_memory(user_id)

async def cleanup_old_memories(max_age_hours: int = 24) -> None:
    """
    오래된 메모리를 정리합니다. (주기적으로 호출하는 것을 권장)
    """
    await memory_manager.cleanup_old_memories(max_age_hours)

# 백그라운드 태스크로 메모리 정리를 주기적으로 실행하는 함수
async def start_memory_cleanup_task():
    """메모리 정리 백그라운드 태스크 시작"""
    while True:
        try:
            await cleanup_old_memories()
            await asyncio.sleep(3600)  # 1시간마다 실행
        except Exception as e:
            logger.error(f"Error in memory cleanup task: {str(e)}")
            await asyncio.sleep(3600)  # 오류 발생 시에도 1시간 후 재시도
