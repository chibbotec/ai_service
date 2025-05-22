import os
import time
import glob
from pathlib import Path
from typing import Dict, Any, Union
from app.schemas.resume import PortfolioData, SystemArchitecture
from dotenv import load_dotenv
from app.utils.progress_tracker import ProgressTracker, ProgressStatus
from app.chain import portfolio_chain
from app.chain import portfolio_role_chain

# 환경변수 로드
load_dotenv()

# 포트폴리오 생성 상태를 저장할 딕셔너리
portfolio_trackers: Dict[str, ProgressTracker] = {}

async def get_portfolio_status(user_id: str) -> Dict[str, Any]:
    """포트폴리오 생성 상태를 조회합니다."""
    if user_id not in portfolio_trackers:
        return {"error": "포트폴리오 생성 요청을 찾을 수 없습니다."}
    
    tracker = portfolio_trackers[user_id]
    progress = tracker.get_progress()
    
    if progress["completed"] == progress["total"]:
        if progress["failed"] > 0:
            return {"error": "포트폴리오 생성 실패"}
        return {
            "status": "completed",
            "result": progress.get("result"),
            "message": progress.get("message", "포트폴리오 생성이 완료되었습니다.")
        }
    else:
        return {
            "status": "processing",
            "progress": progress,
            "current_step": progress.get("current_step", "portfolio_generation"),
            "message": progress.get("message", "포트폴리오 생성 중입니다."),
            "elapsed_time": time.time() - progress.get("start_time", time.time())
        }
    
async def generate_portfolio(user_id: str, repositories: list, commit_files: list) -> Union[PortfolioData, Dict[str, Any]]:
    start_time = time.time()
    
    try:
        # ProgressTracker 초기화
        tracker = ProgressTracker(
            total=len(repositories),
            log_prefix=f"포트폴리오 생성 (사용자: {user_id})"
        )
        tracker.progress["start_time"] = start_time
        portfolio_trackers[user_id] = tracker
        
        if not repositories:
            await tracker.update(ProgressStatus.FAILED, {"error": "분석할 저장소가 없습니다."})
            return {"error": "분석할 저장소가 없습니다."}
            
        code_contents = []
        for repo_path in repositories:
            try:
                # 전체 저장소 경로 구성
                full_repo_path = Path("repository/data") / repo_path
                print(f"저장소 경로: {full_repo_path}")
                
                # 저장소 내의 모든 파일 검색
                for file_path in full_repo_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in [
                        '.py', '.java', '.js', '.html', '.css', '.ts', '.jsx', '.tsx'
                    ]:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                # 파일이 너무 크면 일부만 사용
                                if len(content) > 5000:
                                    content = content[:5000] + "\n... (내용 생략) ..."
                                
                                code_contents.append({
                                    "file": str(file_path.relative_to(full_repo_path)),
                                    "content": content
                                })
                                print(f"파일 처리됨: {file_path.name}")
                        except Exception as e:
                            print(f"파일 읽기 오류 {file_path}: {str(e)}")
                            await tracker.update(ProgressStatus.FAILED, {"error": str(e)})
            except Exception as e:
                print(f"저장소 처리 오류 {repo_path}: {str(e)}")
                await tracker.update(ProgressStatus.FAILED, {"error": str(e)})
        
        if not code_contents:
            await tracker.update(ProgressStatus.FAILED, {"error": "처리 가능한 소스 코드 파일이 없습니다."})
            return {"error": "처리 가능한 소스 코드 파일이 없습니다."}

        # 소스 코드 텍스트 생성
        source_code_text = "\n\n".join([
            f"=== {file['file']} ===\n{file['content']}" 
            for file in code_contents
        ])
        
        # LangChain 체인으로 포트폴리오 생성
        try:
            # 포트폴리오 생성 시작 상태 업데이트
            await tracker.update(ProgressStatus.IN_PROGRESS, {
                "current_step": "portfolio_generation",
                "message": "포트폴리오 생성 중입니다."
            })
            
            response = portfolio_chain.invoke({"source_code": source_code_text})
            processing_time = time.time() - start_time
            print(f"포트폴리오 생성 시간: {processing_time:.2f}초")
            
            # 주요 역할 생성 시작 상태 업데이트
            await tracker.update(ProgressStatus.IN_PROGRESS, {
                "current_step": "role_generation",
                "message": "주요 역할 업데이트 중입니다."
            })

            # 포트폴리오 주요역할 생성
            try:
                role_response = await generate_portfolio_roles(
                    source_code_text=source_code_text,
                    commit_files=commit_files
                )
                
                # 결과 구조화
                structured_response = {
                    "portfolio": response.model_dump() if isinstance(response, PortfolioData) else response,
                    "roles": role_response
                }
                
                # 최종 성공 상태 업데이트
                await tracker.update(ProgressStatus.SUCCESS, {
                    "current_step": "completed",
                    "message": "포트폴리오 생성이 완료되었습니다.",
                    "result": structured_response
                })
                
                return structured_response
            except Exception as role_error:
                print(f"주요 역할 생성 중 오류: {str(role_error)}")
                # 주요 역할 생성 실패는 전체 프로세스를 실패시키지 않음
                structured_response = {
                    "portfolio": response.model_dump() if isinstance(response, PortfolioData) else response,
                    "roles_error": str(role_error)
                }
                await tracker.update(ProgressStatus.SUCCESS, {
                    "current_step": "completed",
                    "message": "포트폴리오 생성이 완료되었습니다. (주요 역할 생성 실패)",
                    "result": structured_response
                })
                return structured_response
        except Exception as e:
            error_msg = f"포트폴리오 생성 실패: {str(e)}"
            print(error_msg)
            
            # 실패 상태 업데이트
            if user_id in portfolio_trackers:
                await portfolio_trackers[user_id].update(ProgressStatus.FAILED, {"error": error_msg})
            
            return {
                "error": error_msg,
                "processing_time": time.time() - start_time
            }
    except Exception as e:
        error_msg = f"포트폴리오 생성 실패: {str(e)}"
        print(error_msg)
        
        # 실패 상태 업데이트
        if user_id in portfolio_trackers:
            await portfolio_trackers[user_id].update(ProgressStatus.FAILED, {"error": error_msg})
        
        return {
            "error": error_msg,
            "processing_time": time.time() - start_time
        }
    
async def generate_portfolio_roles(source_code_text: str, commit_files: list) -> Dict[str, Any]:
    try:
        # LangChain을 사용하여 코드 분석 및 역할 생성
        roles = portfolio_role_chain.invoke({
            "source_code": source_code_text,
            "commit_files": commit_files
        })
        
        return roles
    except Exception as e:
        raise Exception(f"주요 역할 생성 실패: {str(e)}")