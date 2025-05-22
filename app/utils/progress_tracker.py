from typing import Dict, Optional, Callable
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ProgressStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"

class ProgressTracker:
    def __init__(
        self, 
        total: int, 
        log_interval: int = 10,
        status_callback: Optional[Callable[[Dict], None]] = None,
        log_prefix: str = "Progress"
    ):
        self.progress = {
            "total": total,
            "completed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "in_progress": 0
        }
        self.log_interval = log_interval
        self.lock = asyncio.Lock()
        self.status_callback = status_callback
        self.log_prefix = log_prefix

    async def update(self, status: ProgressStatus, metadata: Optional[Dict] = None):
        """진행 상황 업데이트
        
        Args:
            status: 진행 상태 (SUCCESS, FAILED, SKIPPED, IN_PROGRESS)
            metadata: 추가 메타데이터 (선택사항)
        """
        async with self.lock:
            if status == ProgressStatus.IN_PROGRESS:
                # IN_PROGRESS 상태일 때는 completed를 증가시키지 않고 in_progress만 증가
                self.progress["in_progress"] += 1
            else:
                # 다른 상태일 때는 completed를 증가시키고, 이전에 IN_PROGRESS였다면 감소
                if self.progress["in_progress"] > 0:
                    self.progress["in_progress"] -= 1
                self.progress["completed"] += 1
                self.progress[status.value] += 1
            
            # metadata를 progress 딕셔너리에 저장
            if metadata:
                self.progress.update(metadata)
            
            percent = (self.progress["completed"] / self.progress["total"]) * 100
            if percent % self.log_interval < 0.5 and percent > 0:
                self._log_progress(metadata)

            if self.status_callback:
                self.status_callback(self.progress)

    def _log_progress(self, metadata: Optional[Dict] = None):
        """진행 상황 로깅"""
        log_message = (
            f"{self.log_prefix}: {self.progress['completed']}/{self.progress['total']} "
            f"({(self.progress['completed'] / self.progress['total'] * 100):.1f}%), "
            f"성공: {self.progress['success']}, "
            f"실패: {self.progress['failed']}, "
            f"건너뜀: {self.progress['skipped']}, "
            f"진행중: {self.progress['in_progress']}"
        )
        
        if metadata:
            log_message += f" | 메타데이터: {metadata}"
            
        logger.info(log_message)

    def get_progress(self) -> Dict:
        """현재 진행 상황 반환"""
        return self.progress.copy()

    def reset(self):
        """진행 상황 초기화"""
        self.progress = {
            "total": self.progress["total"],
            "completed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "in_progress": 0
        }