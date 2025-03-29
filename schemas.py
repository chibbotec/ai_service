# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# 면접 질문 입력 스키마 (수정됨)
class InterviewQuestionInput(BaseModel):
  """AI 면접 답변 생성을 위한 입력 스키마"""
  questionId: str
  questionText: str  # 질문 내용 추가
  techClass: str = Field(default="Technology")  # 기술 분류 필드 추가

  class Config:
    schema_extra = {
      "example": {
        "questionId": "67de37dc19da0d630ff94a1b",
        "questionText": "MongoDB의 인덱싱에 대해 설명해주세요.",
        "techClass": "Database"
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