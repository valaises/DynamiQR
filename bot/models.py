from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from .database import Base


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    username = Column(String, index=True, nullable=True, unique=True)
    fullname = Column(String, index=True, nullable=True, unique=False)
    active = Column(Boolean, index=True, default=True)

