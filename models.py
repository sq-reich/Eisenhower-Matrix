from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", uselist=False, back_populates="task", cascade="all, delete")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    importance = Column(Boolean, nullable=False)
    urgency = Column(Boolean, nullable=False)
    completed = Column(Boolean, default=False)

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    task = relationship("Task", back_populates="property")
