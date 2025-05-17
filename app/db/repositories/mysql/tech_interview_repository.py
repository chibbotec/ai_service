from sqlalchemy.orm import Session
from app.db.mysql.models import TechInterview
from typing import List, Optional

class TechInterviewRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, tech_interview: TechInterview) -> TechInterview:
        self.db_session.add(tech_interview)
        self.db_session.commit()
        self.db_session.refresh(tech_interview)
        return tech_interview

    def get_by_id(self, tech_interview_id: int) -> Optional[TechInterview]:
        return self.db_session.query(TechInterview).filter(TechInterview.id == tech_interview_id).first()

    def get_all(self) -> List[TechInterview]:
        return self.db_session.query(TechInterview).all()

    def update(self, tech_interview: TechInterview) -> TechInterview:
        try:
            # 기존 엔티티를 가져와서 업데이트
            existing = self.db_session.query(TechInterview).filter(TechInterview.id == tech_interview.id).first()
            if existing:
                for key, value in tech_interview.__dict__.items():
                    if not key.startswith('_'):
                        setattr(existing, key, value)
                self.db_session.commit()
                self.db_session.refresh(existing)
                return existing
            return None
        except Exception as e:
            self.db_session.rollback()
            raise e

    def delete(self, tech_interview_id: int) -> bool:
        tech_interview = self.get_by_id(tech_interview_id)
        if tech_interview:
            self.db_session.delete(tech_interview)
            self.db_session.commit()
            return True
        return False

    def get_by_tech_class(self, tech_class: int) -> List[TechInterview]:
        return self.db_session.query(TechInterview).filter(TechInterview.tech_class == tech_class).all() 