from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    due_date = Column(Date, nullable=True)
    priority = Column(String, default="medium")
    complete = Column(Boolean, default=False)

