from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    link_limit = Column(Integer, default=3)


class UserLink(Base):
    __tablename__ = 'user_link'

    link_id = Column(Integer, index=True, unique=True, primary_key=True, nullable=False)
    owner_id = Column(Integer, index=True, unique=False, nullable=False)
    link_text = Column(String, index=True, default='https://google.com', unique=False)


class UserLinkActions(Base):
    __tablename__ = 'user_link_actions'

    id = Column(String, index=True, primary_key=True, nullable=False)
    link_id = Column(Integer, index=True, unique=False, nullable=False)
    owner_id = Column(Integer, index=True, unique=False, nullable=False)
    action_time = Column(String, unique=False, nullable=False)


