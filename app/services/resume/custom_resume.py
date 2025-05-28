import time
from app.schemas.resume import CustomResumeRequest, CustomResumeResponse, JobAnalysis, ResumeDetail
from dotenv import load_dotenv
from typing import Dict, Any, Union, Optional
from app.utils.progress_tracker import ProgressTracker, ProgressStatus
from app.chain.custom_resume_chain import (
    generate_start,
    generate_tech_stack,
    generate_coverletter,
    clear_user_memory
)
from langchain.memory import ConversationBufferMemory
import logging

load_dotenv()
logger = logging.getLogger(__name__)

custom_resume_trackers: Dict[str, ProgressTracker] = {}

def preprocess_request_data(request: CustomResumeRequest) -> Dict[str, Any]:
    """
    CustomResumeRequest 데이터를 전처리하여 필요한 정보만 추출합니다.
    """
    processed_data = {
        "type": request.type,
        "job_description": "",
        "additional_info": request.additionalInfo or ""
    }
    
    # 채용 공고 정보 처리
    if request.jobDescription:
        job_info = []
        job_desc = request.jobDescription
        if hasattr(job_desc, '__dict__'):
            job_desc = job_desc.__dict__ if hasattr(job_desc, '__dict__') else job_desc
        if isinstance(job_desc, dict):
            if job_desc.get("company"):
                job_info.append(f"회사: {job_desc['company']}")
            if job_desc.get("position"):
                job_info.append(f"직무: {job_desc['position']}")
            if job_desc.get("career"):
                job_info.append(f"경력: {job_desc['career']}")
            if job_desc.get("mainTasks") and len(job_desc["mainTasks"]) > 0:
                job_info.append("\n주요 업무:")
                for task in job_desc["mainTasks"]:
                    job_info.append(f"- {task}")
            if job_desc.get("requirements") and len(job_desc["requirements"]) > 0:
                job_info.append("\n요구사항:")
                for req in job_desc["requirements"]:
                    job_info.append(f"- {req}")
            if job_desc.get("resumeRequirements") and len(job_desc["resumeRequirements"]) > 0:
                job_info.append("\n이력서 요구사항:")
                for req in job_desc["resumeRequirements"]:
                    job_info.append(f"- {req}")
            if job_desc.get("recruitmentProcess") and len(job_desc["recruitmentProcess"]) > 0:
                job_info.append("\n채용 프로세스:")
                for process in job_desc["recruitmentProcess"]:
                    job_info.append(f"- {process}")
        else:
            if hasattr(job_desc, 'company') and job_desc.company:
                job_info.append(f"회사: {job_desc.company}")
            if hasattr(job_desc, 'position') and job_desc.position:
                job_info.append(f"직무: {job_desc.position}")
            if hasattr(job_desc, 'career') and job_desc.career:
                job_info.append(f"경력: {job_desc.career}")
            if hasattr(job_desc, 'mainTasks') and job_desc.mainTasks and len(job_desc.mainTasks) > 0:
                job_info.append("\n주요 업무:")
                for task in job_desc.mainTasks:
                    job_info.append(f"- {task}")
            if hasattr(job_desc, 'requirements') and job_desc.requirements and len(job_desc.requirements) > 0:
                job_info.append("\n요구사항:")
                for req in job_desc.requirements:
                    job_info.append(f"- {req}")
            if hasattr(job_desc, 'resumeRequirements') and job_desc.resumeRequirements and len(job_desc.resumeRequirements) > 0:
                job_info.append("\n이력서 요구사항:")
                for req in job_desc.resumeRequirements:
                    job_info.append(f"- {req}")
        processed_data["job_description"] = "\n".join(job_info)
    
    # type에 따라 이력서 또는 포트폴리오 정보 처리
    if request.type == "resume" and request.selectedResume:
        resume_info = []
        resume = request.selectedResume
        if hasattr(resume, '__dict__'):
            resume_dict = resume.__dict__ if hasattr(resume, '__dict__') else resume
        elif isinstance(resume, dict):
            resume_dict = resume
        else:
            resume_dict = {}
        title = resume_dict.get('title') or getattr(resume, 'title', None)
        if title:
            resume_info.append(f"이력서 제목: {title}")
        tech_stack = resume_dict.get('techStack') or getattr(resume, 'techStack', None)
        if tech_stack:
            resume_info.append(f"보유 기술: {', '.join(tech_stack)}")
        tech_summary = resume_dict.get('techSummary') or getattr(resume, 'techSummary', None)
        if tech_summary:
            resume_info.append(f"기술 요약: {tech_summary}")
        careers = resume_dict.get('careers') or getattr(resume, 'careers', None)
        if careers and len(careers) > 0:
            resume_info.append("\n경력 사항:")
            for career in careers:
                if isinstance(career, dict):
                    position = career.get('position', '')
                    company = career.get('company', '')
                    period = career.get('period', '')
                    achievement = career.get('achievement', '')
                else:
                    position = getattr(career, 'position', '')
                    company = getattr(career, 'company', '')
                    period = getattr(career, 'period', '')
                    achievement = getattr(career, 'achievement', '')
                resume_info.append(f"- {position} ({company})")
                if period:
                    resume_info.append(f"  기간: {period}")
                if achievement:
                    resume_info.append(f"  성과: {achievement}")
        projects = resume_dict.get('projects') or getattr(resume, 'projects', None)
        if projects and len(projects) > 0:
            resume_info.append("\n프로젝트:")
            for project in projects:
                if isinstance(project, dict):
                    name = project.get('name', '')
                    member_roles = project.get('memberRoles', '')
                    role = project.get('role', '')
                    tech_stack = project.get('techStack', [])
                    description = project.get('description', '')
                    github_link = project.get('githubLink', '')
                    deploy_link = project.get('deployLink', '')
                else:
                    name = getattr(project, 'name', '')
                    member_roles = getattr(project, 'memberRoles', '')
                    role = getattr(project, 'role', '')
                    tech_stack = getattr(project, 'techStack', [])
                    description = getattr(project, 'description', '')
                    github_link = getattr(project, 'githubLink', '')
                    deploy_link = getattr(project, 'deployLink', '')
                if name:
                    resume_info.append(f"- {name}")
                if member_roles:
                    resume_info.append(f"  맡은 역할: {member_roles}")
                if role:
                    resume_info.append(f"  주요 역할 및 성과: {role}")
                if tech_stack:
                    resume_info.append(f"  기술 스택: {', '.join(tech_stack)}")
                if description:
                    resume_info.append(f"  설명: {description}")
                if github_link:
                    resume_info.append(f"  GitHub: {github_link}")
                if deploy_link:
                    resume_info.append(f"  배포 링크: {deploy_link}")
        processed_data["resume_info"] = "\n".join(resume_info)
    elif request.type == "portfolio" and request.selectedPortfolio:
        portfolio_info = []
        for portfolio in request.selectedPortfolio:
            if hasattr(portfolio, 'title') and portfolio.title:
                portfolio_info.append(f"\n포트폴리오 제목: {portfolio.title}")
            if hasattr(portfolio, 'memberRoles') and portfolio.memberRoles:
                portfolio_info.append(f"담당 역할: {portfolio.memberRoles}")
            if hasattr(portfolio, 'contents') and portfolio.contents:
                contents = portfolio.contents
                if hasattr(contents, 'summary') and contents.summary:
                    portfolio_info.append(f"\n프로젝트 요약: {contents.summary}")
                if hasattr(contents, 'description') and contents.description:
                    portfolio_info.append(f"프로젝트 개요: {contents.description}")
                if hasattr(contents, 'techStack') and contents.techStack:
                    portfolio_info.append(f"사용 기술: {contents.techStack}")
                if hasattr(contents, 'roles') and contents.roles:
                    portfolio_info.append(f"주요 역할: {', '.join(contents.roles)}")
                if hasattr(contents, 'features') and contents.features:
                    portfolio_info.append("\n주요 기능:")
                    for feature, descriptions in contents.features.items():
                        portfolio_info.append(f"- {feature}:")
                        for desc in descriptions:
                            portfolio_info.append(f"  * {desc}")
                if hasattr(contents, 'architecture') and contents.architecture:
                    portfolio_info.append("\n아키텍처:")
                    if hasattr(contents.architecture, 'communication'):
                        portfolio_info.append(f"- 통신 방식: {contents.architecture.communication}")
                    if hasattr(contents.architecture, 'deployment'):
                        portfolio_info.append(f"- 배포 구조: {contents.architecture.deployment}")
            portfolio_info.append("\n" + "="*50 + "\n")
        processed_data["portfolio_info"] = "\n".join(portfolio_info)
    logger.info(f"Processed data for user: {processed_data}")
    return processed_data

async def get_custom_resume_status(user_id: str) -> Dict[str, Any]:
    """커스텀 이력서 생성 상태 조회"""
    if user_id not in custom_resume_trackers:
        return {"error": "커스텀 이력서 생성 요청을 찾을 수 없습니다."}
    
    tracker = custom_resume_trackers[user_id]
    progress = tracker.get_progress()

    if progress.get("success", 0) > 0 or progress.get("result"):
        if progress["failed"] > 0:
            return {"error": "커스텀 이력서 생성 실패"}
        return {
            "status": "completed",
            "result": progress.get("result"),
            "message": progress.get("message", "커스텀 이력서 생성이 완료되었습니다.")
        }
    else:
        return {
            "status": "processing",
            "progress": progress,
            "current_step": progress.get("current_step", "custom_resume_generation"),
            "message": progress.get("message", "커스텀 이력서 생성 중입니다."),
            "elapsed_time": time.time() - progress.get("start_time", time.time())
        }
    
async def generate_custom_resume(user_id: str, request: CustomResumeRequest) -> Union[CustomResumeResponse, Dict[str, Any]]:
    """커스텀 이력서 생성"""
    start_time = time.time()
    logger.info(f"Starting custom resume generation for user: {user_id}")

    try:
        # 이전 메모리 초기화
        clear_user_memory(user_id)
        
        # ProgressTracker 초기화
        tracker = ProgressTracker(
            total=4,  # 총 4단계: start, tech_stack, cover_letter, completed
            log_interval=10,
            log_prefix="Custom Resume Generation"
        )
        custom_resume_trackers[user_id] = tracker

        try:
            # 데이터 전처리
            logger.info("Preprocessing request data...")
            processed_data = preprocess_request_data(request)
            
            # 데이터 검증
            if not processed_data.get("job_description"):
                raise ValueError("채용 공고 정보가 없습니다.")
            
            if not processed_data.get("resume_info") and not processed_data.get("portfolio_info"):
                raise ValueError("이력서 또는 포트폴리오 정보가 없습니다.")
            
            # 각 단계별 생성
            response_position = ""
            if request.jobDescription:
                if hasattr(request.jobDescription, 'position'):
                    response_position = request.jobDescription.position
                elif isinstance(request.jobDescription, dict):
                    response_position = request.jobDescription.get("position", "")

            logger.info("Generating start response...")
            response_start = await generate_start(
                processed_data=processed_data,
                tracker=tracker,
                user_id=user_id
            )

            logger.info("Generating tech stack analysis...")
            response_tech_stack = await generate_tech_stack(
                processed_data=processed_data,
                tracker=tracker,
                user_id=user_id
            )

            logger.info("Generating cover letter...")
            response_coverletter = await generate_coverletter(
                processed_data=processed_data,
                tracker=tracker,
                user_id=user_id
            )
            
            # 결과 구성
            result = {
                "position": response_position,
                "tech_stack": {
                    "tech_stack": response_tech_stack.tech_stack,
                    "tech_capabilities": response_tech_stack.tech_capabilities
                },
                "cover_letter": {
                    "coverLetter": [
                        {
                            "title": section.title,
                            "content": section.content
                        } for section in response_coverletter.coverLetter
                    ]
                }
            }
            
            logger.info("Custom resume generation completed successfully")
            await tracker.update(
                status=ProgressStatus.SUCCESS,
                metadata={
                    "current_step": "completed",
                    "result": result,
                    "message": "커스텀 이력서 생성이 완료되었습니다."
                }
            )
            
            return CustomResumeResponse(
                status="success",
                result=result,
                message="커스텀 이력서가 성공적으로 생성되었습니다."
            )
            
        except Exception as e:
            logger.error(f"Error during custom resume generation: {str(e)}")
            await tracker.update(
                status=ProgressStatus.FAILED,
                metadata={
                    "current_step": "failed",
                    "message": f"커스텀 이력서 생성 중 오류가 발생했습니다: {str(e)}"
                }
            )
            return {
                "error": str(e),
                "status": "failed"
            }
            
    except Exception as e:
        logger.error(f"Critical error in generate_custom_resume: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }