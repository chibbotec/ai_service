from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, CheckConstraint, Boolean, JSON, SmallInteger, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

class Submit(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"  # 진행중
    COMPLETED = "COMPLETED"      # 제출완료
    EVALUATED = "EVALUATED"      # 평가완료

    @property
    def value_int(self):
        values = {
            self.IN_PROGRESS: 0,
            self.COMPLETED: 1,
            self.EVALUATED: 2
        }
        return values[self]

class TechClass(enum.Enum):
    JAVASCRIPT = 0
    TYPESCRIPT = 1
    REACT = 2
    VUE = 3
    ANGULAR = 4
    NODE_JS = 5
    JAVA = 6
    SPRING = 7
    PYTHON = 8
    DJANGO = 9
    DATABASE = 10
    DEVOPS = 11
    MOBILE = 12
    ALGORITHM = 13
    COMPUTER_SCIENCE = 14
    OS = 15
    NETWORK = 16
    SECURITY = 17
    CLOUD = 18
    ETC = 19

    @property
    def display_name(self):
        display_names = {
            self.JAVASCRIPT: "JavaScript",
            self.TYPESCRIPT: "TypeScript",
            self.REACT: "React",
            self.VUE: "Vue",
            self.ANGULAR: "Angular",
            self.NODE_JS: "Node.js",
            self.JAVA: "Java",
            self.SPRING: "Spring",
            self.PYTHON: "Python",
            self.DJANGO: "Django",
            self.DATABASE: "Database",
            self.DEVOPS: "DevOps",
            self.MOBILE: "Mobile",
            self.ALGORITHM: "Algorithm",
            self.COMPUTER_SCIENCE: "Computer Science",
            self.OS: "OS",
            self.NETWORK: "Network",
            self.SECURITY: "Security",
            self.CLOUD: "Cloud",
            self.ETC: "ETC"
        }
        return display_names[self]

Base = declarative_base()

class Contest(Base):
    __tablename__ = 'contest'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6))
    space_id = Column(BigInteger)
    submit = Column(SmallInteger)
    timeout_millis = Column(BigInteger)
    title = Column(String(255))
    
    # Relationships
    participants = relationship("Participant", back_populates="contest")
    problems = relationship("Problem", back_populates="contest")
    
    __table_args__ = (
        CheckConstraint('submit between 0 and 2', name='contest_chk_1'),
    )

    @property
    def submit_status(self):
        if self.submit == 0:
            return Submit.IN_PROGRESS
        elif self.submit == 1:
            return Submit.COMPLETED
        elif self.submit == 2:
            return Submit.EVALUATED
        return None

class Problem(Base):
    __tablename__ = 'problem'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contest_id = Column(BigInteger, ForeignKey('contest.id'))
    tech_interview_id = Column(BigInteger, ForeignKey('tech_interview.id'))
    
    # Relationships
    contest = relationship("Contest", back_populates="problems")
    tech_interview = relationship("TechInterview", back_populates="problems")
    answers = relationship("Answer", back_populates="problem")

class Participant(Base):
    __tablename__ = 'participant'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(BigInteger)
    nickname = Column(String(255))
    submit = Column(SmallInteger)
    contest_id = Column(BigInteger, ForeignKey('contest.id'))
    
    # Relationships
    contest = relationship("Contest", back_populates="participants")
    answers = relationship("Answer", back_populates="participant")
    
    __table_args__ = (
        CheckConstraint('submit between 0 and 2', name='participant_chk_1'),
    )

    @property
    def submit_status(self):
        if self.submit == 0:
            return Submit.IN_PROGRESS
        elif self.submit == 1:
            return Submit.COMPLETED
        elif self.submit == 2:
            return Submit.EVALUATED
        return None

class Answer(Base):
    __tablename__ = 'answer'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    answer = Column(Text)
    feedback = Column(Text)
    rank_score = Column(Integer, nullable=False)
    participant_id = Column(BigInteger, ForeignKey('participant.id'))
    problem_id = Column(BigInteger, ForeignKey('problem.id'))
    
    # Relationships
    participant = relationship("Participant", back_populates="answers")
    problem = relationship("Problem", back_populates="answers")

class TechInterview(Base):
    __tablename__ = "tech_interview"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    additional_topics = Column(Text)
    ai_answer = Column(Text)
    key_point = Column(Text)
    question = Column(String(255))
    tech_class = Column(SmallInteger)

    # Relationship with Problem
    problems = relationship("Problem", back_populates="tech_interview")

    __table_args__ = (
        CheckConstraint('tech_class between 0 and 19', name='tech_interview_chk_1'),
    )

    @property
    def tech_class_enum(self):
        if self.tech_class is None:
            return None
        return TechClass(self.tech_class)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(String(255), nullable=False)
    question_text = Column(Text, nullable=False)
    tech_class = Column(String(255), nullable=False)
    answers = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParticipantQna(Base):
    __tablename__ = "participant_qnas"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(255), nullable=False)
    participant_id = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(255), nullable=False)
    participant_id = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
