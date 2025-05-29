import time
from app.schemas.resume import CustomResumeRequest, CustomResumeResponse, JobAnalysis
from dotenv import load_dotenv
from typing import Dict, Any, Union, Optional
from app.utils.progress_tracker import ProgressTracker, ProgressStatus
from app.chain.custom_resume_chain import (
    generate_start,
    generate_tech_stack,
    generate_coverletter,
    clear_user_memory,
    generate_portfolio,
    generate_career
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
    
    if request.selectedPortfolios:
        portfolio_info = []
        for portfolio in request.selectedPortfolios:
            if hasattr(portfolio, 'title') and portfolio.title:
                portfolio_info.append(f"\n포트폴리오 제목: {portfolio.title}")
            if hasattr(portfolio, 'memberRoles') and portfolio.memberRoles:
                portfolio_info.append(f"담당 역할: {portfolio.memberRoles}")
            if hasattr(portfolio, 'memberCount') and portfolio.memberCount:
                portfolio_info.append(f"참여 인원 수: {portfolio.memberCount}")
            if hasattr(portfolio, 'startDate') and portfolio.startDate:
                portfolio_info.append(f"시작일: {portfolio.startDate}")
            if hasattr(portfolio, 'endDate') and portfolio.endDate:
                portfolio_info.append(f"종료일: {portfolio.endDate}")
            if hasattr(portfolio, 'githubLink') and portfolio.githubLink:
                portfolio_info.append(f"GitHub 링크: {portfolio.githubLink}")
            if hasattr(portfolio, 'deployLink') and portfolio.deployLink:
                portfolio_info.append(f"배포 링크: {portfolio.deployLink}")
            
            if hasattr(portfolio, 'contents') and portfolio.contents:
                contents = portfolio.contents
                if contents.summary:
                    portfolio_info.append(f"\n프로젝트 요약: {contents.summary}")
                if contents.description:
                    portfolio_info.append(f"프로젝트 개요: {contents.description}")
                if contents.techStack:
                    portfolio_info.append(f"사용 기술: {contents.techStack}")
                if contents.roles:
                    portfolio_info.append(f"주요 역할: {', '.join(contents.roles)}")
                if contents.features:
                    portfolio_info.append("\n주요 기능:")
                    for feature, descriptions in contents.features.items():
                        portfolio_info.append(f"- {feature}:")
                        for desc in descriptions:
                            portfolio_info.append(f"  * {desc}")
                if contents.architecture:
                    portfolio_info.append("\n아키텍처:")
                    portfolio_info.append(f"- 통신 방식: {contents.architecture.communication}")
                    portfolio_info.append(f"- 배포 구조: {contents.architecture.deployment}")
            portfolio_info.append("\n" + "="*50 + "\n")
        processed_data["portfolio_info"] = "\n".join(portfolio_info)

    if request.careers:
        career_info = []
        for career in request.careers:
            if career.company:
                career_info.append(f"회사: {career.company}")
            if career.position:
                career_info.append(f"직무: {career.position}")
            if career.startDate:
                career_info.append(f"시작일: {career.startDate}")
            if career.endDate:
                career_info.append(f"종료일: {career.endDate}")
            if career.isCurrent:
                career_info.append("현재 재직 중")
            if career.description:
                career_info.append(f"업무 설명: {career.description}")
            if career.achievement:
                career_info.append(f"주요 성과: {career.achievement}")
            career_info.append("\n" + "-"*30 + "\n")
        processed_data["career_info"] = "\n".join(career_info)

    logger.info(f"Processed data for user: {processed_data}")
    return processed_data

async def get_custom_resume_status(user_id: str) -> Dict[str, Any]:
    """커스텀 이력서 생성 상태 조회"""
    logger.info(f"Checking custom resume status for user: {user_id}")
    logger.info(f"Available trackers: {list(custom_resume_trackers.keys())}")
    
    if user_id not in custom_resume_trackers:
        logger.error(f"Tracker not found for user: {user_id}")
        return {"error": "커스텀 이력서 생성 요청을 찾을 수 없습니다."}
    
    tracker = custom_resume_trackers[user_id]
    progress = tracker.get_progress()
    logger.info(f"Progress for user {user_id}: {progress}")

    # 모든 단계가 완료되었는지 확인
    completed_steps = progress.get("completed_steps", [])
    all_steps_completed = len(completed_steps) == 5 and all(step in completed_steps for step in ["start", "portfolio", "career", "tech_stack", "cover_letter"])

    if all_steps_completed and progress.get("result"):
        if progress["failed"] > 0:
            return {"error": "커스텀 이력서 생성 실패"}
        return {
            "status": "completed",
            "result": progress.get("result"),
            "message": progress.get("message", "커스텀 이력서 생성이 완료되었습니다.")
        }
    else:
        # 현재 진행 중인 단계 확인
        current_step = progress.get("current_step", "custom_resume_generation")
        step_status = {
            "start": "completed" if "start" in completed_steps else "waiting",
            "portfolio": "completed" if "portfolio" in completed_steps else "waiting",
            "career": "completed" if "career" in completed_steps else "waiting",
            "tech_stack": "completed" if "tech_stack" in completed_steps else "waiting",
            "cover_letter": "completed" if "cover_letter" in completed_steps else "waiting"
        }
        
        # 현재 진행 중인 단계 표시
        if current_step in step_status:
            step_status[current_step] = "processing"
        
        return {
            "status": "processing",
            "progress": progress,
            "current_step": current_step,
            "step_status": step_status,
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
            total=5,  # Updated to include all steps: start, portfolio, career, tech_stack, cover_letter
            log_interval=10,
            log_prefix="Custom Resume Generation"
        )
        custom_resume_trackers[user_id] = tracker
        logger.info(f"Initialized tracker for user: {user_id}")
        logger.info(f"Current trackers: {list(custom_resume_trackers.keys())}")

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

            response_portfolio = await generate_portfolio(
                processed_data=processed_data,
                tracker=tracker,
                user_id=user_id
            )

            # 경력 정보가 있는 경우에만 경력 분석 실행
            response_career = None
            if request.careers:
                response_career = await generate_career(
                    processed_data=processed_data,
                    tracker=tracker,
                    user_id=user_id
                )
            else:
                # 경력 정보가 없는 경우 해당 단계 완료 처리
                progress = tracker.get_progress()
                completed_steps = progress.get("completed_steps", [])
                completed_steps.append("career")
                await tracker.update(
                    status=ProgressStatus.SUCCESS,
                    metadata={
                        "current_step": "career",
                        "completed_steps": completed_steps,
                        "message": "경력 정보가 없어 해당 단계를 건너뜁니다."
                    }
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
                "portfolio": response_portfolio,
                "tech_stack": {
                    "tech_stack": response_tech_stack.tech_stack,
                    "tech_summary": response_tech_stack.tech_summary
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
            
            # 경력 정보가 있는 경우에만 결과에 추가
            if response_career:
                result["career"] = response_career
            
            logger.info("Custom resume generation completed successfully")
            logger.info(f"Final result for user {user_id}: {result}")
            
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