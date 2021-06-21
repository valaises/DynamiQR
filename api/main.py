from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from fastapi.responses import HTMLResponse
from uuid import uuid4

import crud
import models
from database import SessionLocal, engine
from schemas import User, UserLink

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/create_user')
async def create_user(user: User, db: Session = Depends(get_db)):
    crud.create_user(db=db, id=user.user_id, link_limit=user.link_limit)
    if crud.get_user(db=db, id=user.user_id):
        return HTTPException(status_code=status.HTTP_201_CREATED)


@app.post('/add_link')
async def add_link(user_link: UserLink, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, id=user_link.owner_id)
    if user.link_limit == 0:
        return HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED)
    crud.create_link(db=db, link_id=user_link.link_id, owner_id=user_link.owner_id, link_text=user_link.link_text)
    crud.update_user(db=db, id=user_link.owner_id, link_limit=user.link_limit-1)
    if crud.get_link(db=db, owner_id=user_link.owner_id, link_id=user_link.link_id):
        return HTTPException(status_code=status.HTTP_201_CREATED)


@app.post('/change_link_text')
async def change_link_text(user_link: UserLink, db: Session = Depends(get_db)):
    crud.update_link(db=db, link_id=user_link.link_id, owner_id=user_link.owner_id, upd_link_text=user_link.link_text)
    if crud.get_link(db=db, owner_id=user_link.owner_id, link_id=user_link.link_id).link_text == user_link.link_text:
        return HTTPException(status_code=status.HTTP_200_OK)


@app.post('/update_limit')
async def update_limit(user_id: int, link_limit: int, db: Session = Depends(get_db)):
    crud.update_user(db=db, id=user_id, link_limit=link_limit)
    if crud.get_user(db=db, id=user_id).link_limit == link_limit:
        return HTTPException(status_code=status.HTTP_200_OK)


@app.get('/user/{user_id}')
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db=db, id=user_id)


@app.get('/user/{user_id}/links/{link_id}', response_class=HTMLResponse)
async def get_link(link_id: int, user_id: int, db: Session = Depends(get_db)):
    link = crud.get_link(db=db, owner_id=user_id, link_id=link_id).link_text
    crud.create_action(db=db, id=uuid4(), link_id=link_id, owner_id=user_id)
    return f'''
    <html>
        <head></head>
        <body>
            <script type="text/javascript">
                window.location.href = "{link}";
            </script>
        </body>
    </html>
    '''

@app.get('/user/{user_id}/stats/{link_id}')
async def get_stats(link_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.get_actions(db=db, link_id=link_id, owner_id=user_id)

@app.get('/user/{user_id}/links_list')
async def get_links(user_id, db: Session = Depends(get_db)):
    return crud.get_links(db=db, owner_id=user_id)
