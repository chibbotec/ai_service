from datetime import datetime
from typing import Dict, List, Any, Optional

# 질문 문서 스키마 추가
QUESTION_SCHEMA = {
    "id": "str",                  # 질문 ID (MongoDB ObjectId)
    "spaceId": "int",             # 공간 ID
    "techClass": "str",           # 기술 분류
    "questionText": "str",        # 질문 내용
    "author": {                   # 질문 작성자
        "id": "int",
        "nickname": "str"
    },
    "participants": [             # 참여자 목록
        {
            "id": "int",
            "nickname": "str"
        }
    ],
    "answers": {                  # 답변 맵 (키-값)
        "memberId:[id]": "str",   # 사용자 답변
        "ai": "str"               # AI 답변
    },
    "createdAt": "datetime",      # 생성 시간
    "updatedAt": "datetime"       # 수정 시간
}
