from pydantic import BaseModel

from typing import Optional


class User(BaseModel):
    user_id: int
    link_limit: Optional[int] = 3

    # class Config:
    #     orm_mode = True


class UserLink(BaseModel):
    owner_id: int
    link_id: int
    link_text: Optional[str] = None

    # class Config:
    #     orm_mode = True


class UserLinkActions(BaseModel):
    id: str
    link_id: int
    owner_id: int
    action_time: str
