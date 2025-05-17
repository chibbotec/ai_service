from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# 면접 질문 입력 스키마
class InterviewQuestionInput(BaseModel):
    """AI 면접 답변 생성을 위한 입력 스키마"""
    id: int
    questionText: str
    techClass: str

    class Config:
        schema_extra = {
            "example": {
                "id": 4,
                "questionText": "MongoDB의 인덱싱에 대해 설명해주세요.",
                "techClass": "JAVASCRIPT"
            }
        }

# 면접 답변 출력 스키마
class InterviewAnswer(BaseModel):
    """면접 질문에 대한 AI 답변 스키마"""
    question: str = Field(description="면접에서 질문받은 내용")
    answer: str = Field(description="면접 질문에 대한 모범 답변")
    tips: str = Field(description="면접에서 이 답변을 할 때 강조할 포인트")
    related_topics: str = Field(description="관련 기술/개념 추가 설명")

    class Config:
        schema_extra = {
            "example": {
                "question": "몽고DB에 대해 어떻게 생각하세요?",
                "answer": "MongoDB는 문서 지향 NoSQL 데이터베이스로, JSON과 유사한 BSON 형식으로 데이터를 저장합니다...",
                "tips": "실제 프로젝트에서 MongoDB를 사용한 경험과 관계형 DB와의 비교 분석을 언급하면 좋습니다.",
                "related_topics": "NoSQL, 문서 데이터베이스, 스키마리스 설계, 샤딩, 레플리카셋"
            }
        }

class ParticipantAnswer(BaseModel):
    participant_id: int
    nickname: str
    answer: str
    rank_score: int = 0

class Problem(BaseModel):
    id: int
    problem: str
    ai_answer: str
    answers: List[ParticipantAnswer]

class Contest(BaseModel):
    id: int
    title: str
    problems: List[Problem]

class Evaluation(BaseModel):
    """AI 답변 평가를 위한 스키마"""
    score: int = Field(description="답변의 점수 (0-100)")
    feedback: str = Field(description="답변에 대한 피드백")

    class Config:
        schema_extra = {
            "example": {
                "score": 100,
                "feedback": "응시자는 동기와 비동기 통신의 기본 개념을 이해하고 있는 것으로 보입니다..."
            }
        }

# 기존 면접 관련 스키마들
class TechInterviewBase(BaseModel):
    additional_topics: Optional[str] = None
    ai_answer: Optional[str] = None
    key_point: Optional[str] = None
    question: str
    tech_class: int

class TechInterviewCreate(TechInterviewBase):
    pass

class TechInterviewResponse(TechInterviewBase):
    id: int

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    author_id: int
    author_nickname: str
    space_id: int
    tech_interview_id: int

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ParticipantQnaBase(BaseModel):
    member_id: int
    nickname: str
    question_id: int

class ParticipantQnaCreate(ParticipantQnaBase):
    pass

class ParticipantQnaResponse(ParticipantQnaBase):
    id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    comment: str
    participant_qna_id: int
    question_id: int

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int

    class Config:
        from_attributes = True 