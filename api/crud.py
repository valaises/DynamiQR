from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import models



def get_user(db: Session, id: int):
    return db.query(models.User).filter(models.User.user_id == id).first()


def create_user(db: Session, id: int, link_limit: Optional[int] = 3):
    db_user = models.User(user_id=id, link_limit=link_limit)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def update_user(db: Session, id: int, link_limit: int):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    user.link_limit = link_limit
    db.commit()
    db.refresh(user)


def create_link(db: Session, link_id: int, owner_id: int, link_text: str):
    db_link = models.UserLink(link_id=link_id, owner_id=owner_id, link_text=link_text)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)


def get_links(db: Session, owner_id: int):
    return db.query(models.UserLink).filter_by(owner_id=owner_id).all()


def get_link(db: Session, owner_id: int, link_id: int):
    return db.query(models.UserLink)\
        .filter_by(owner_id=owner_id, link_id=link_id).first()


def update_link(db: Session, owner_id: int, link_id: int, upd_link_text: str):
    link = db.query(models.UserLink)\
        .filter_by(owner_id=owner_id, link_id=link_id).first()
    link.link_text = upd_link_text
    db.commit()
    db.refresh(link)


def create_action(db: Session, id: str, link_id: int, owner_id: int):
    db_action = models.UserLinkActions(id=str(id), link_id=link_id, owner_id=owner_id,
                                       action_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    db.add(db_action)
    db.commit()
    db.refresh(db_action)


def get_actions(db: Session, link_id: int, owner_id: int):
    return db.query(models.UserLinkActions).filter_by(
        link_id=link_id, owner_id=owner_id
    ).all()
