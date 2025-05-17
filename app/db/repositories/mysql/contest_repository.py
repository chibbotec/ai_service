from sqlalchemy.orm import Session
from app.db.mysql.models import Contest
from typing import List, Optional
from datetime import datetime

class ContestRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, contest: Contest) -> Contest:
        if not contest.created_at:
            contest.created_at = datetime.utcnow()
        self.db_session.add(contest)
        self.db_session.commit()
        self.db_session.refresh(contest)
        return contest

    def get_by_id(self, contest_id: int) -> Optional[Contest]:
        return self.db_session.query(Contest).filter(Contest.id == contest_id).first()

    def get_all(self) -> List[Contest]:
        return self.db_session.query(Contest).all()

    def update(self, contest: Contest) -> Contest:
        self.db_session.commit()
        self.db_session.refresh(contest)
        return contest

    def delete(self, contest_id: int) -> bool:
        contest = self.get_by_id(contest_id)
        if contest:
            self.db_session.delete(contest)
            self.db_session.commit()
            return True
        return False

    def get_by_space_id(self, space_id: int) -> List[Contest]:
        return self.db_session.query(Contest).filter(Contest.space_id == space_id).all()

    def get_active_contests(self) -> List[Contest]:
        return self.db_session.query(Contest).filter(Contest.submit == 0).all() 