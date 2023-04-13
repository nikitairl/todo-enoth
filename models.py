from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class ToDo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    task = Column(String)
    completed = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Todo {self.id}>"
