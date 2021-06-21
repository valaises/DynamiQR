from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

import models


def create_user(db: Session, id: int,
                username: Optional[str] = None,
                fullname: Optional[str] = None):
    db_user = models.User(id=id, username=username, fullname=fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def get_user(db: Session, id: int):
    return db.query(models.User).filter_by(id=id).first()


def update_user(db: Session, id: int,
                username: Optional[str] = None,
                fullname: Optional[str] = None,
                active: Optional[bool] = True):
    try:
        user = get_user(db=db, id=id)
        assert user
    except AssertionError:
        create_user(db=db, id=id, username=username, fullname=fullname)
    else:
        user.id, user.username, user.fullname, user.active = id, username, fullname, active
        db.commit()
        db.refresh(user)

