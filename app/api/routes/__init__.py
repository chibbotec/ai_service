from .health import router as health_router
from .coding_test import router as coding_test_router
from .resume import router as resume_router
from .interview import router as interview_router

__all__ = [
    'health_router',
    'coding_test_router',
    'resume_router',
    'interview_router'
]
