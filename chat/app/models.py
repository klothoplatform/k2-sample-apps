from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
