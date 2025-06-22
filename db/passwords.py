from sqlalchemy import Column, Integer, String
from db.base import Base


class Passwords(Base):
    __tablename__ = "passwords"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False)
    password = Column(String, nullable=False)
