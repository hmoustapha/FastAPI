import time
from fastapi import FastAPI, Response, status, HTTPException , Depends # Depend v3
from fastapi.params import Body
from pydantic import BaseModel, ConfigDict  # for schema validation 
from typing import Optional     # for optional field in schema
from random import randrange
# version 2
import psycopg as pgres            # for connecting to postgres
from psycopg.rows import dict_row   # for matching rows in cursor
# version 3 - using Object Relational Mapper (ORM) instead of raw psycopg
# requires opening a session using db engine and model classes
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

# version 3 - only CREATE all tables stated in models / doesn't UPDATE tables 
models.Base.metadata.create_all(bind=engine)

# uvicorn app.main:app --reload     >> for running the fastApi app
#new >> we put main.py in a app folder(a pakage initiated with __init__.py)
# uvicorn app.main:app --reload

# for built-in documentation 
# http://127.0.0.1:8000/docs     >> for Swagger UI doc ready to share
# or
# http://127.0.0.1:8000/redoc     >> diff format

#version 1
app = FastAPI()


# version 1
class Post(BaseModel):  # for schema validation
    model_config = ConfigDict(extra='forbid')   # forbid extra fields from user
    title: str
    content: str                    #required
    published: bool = False         #default value >> optional field for the user 
#    rating: Optional[int]= None     


# version 1 - the @ is a decorater
@app.get("/")   #path operation with http method
async def main_page():
    return {"Post": "Hello World>>>>>>"}

# version 3 - using Object Relational Mapper (ORM) instead of raw psycopg
@app.get("/posts")   #path operation with http method
def fetch_new_1(db: Session = Depends(get_db)):
    orm_posts =  db.query(models.Post).all()
    return {"Post": orm_posts}

# version 3 - using Object Relational Mapper (ORM) instead of raw psycopg
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(payload: Post, db: Session = Depends(get_db)):
    new_post = models.Post(title=payload.title, content=payload.content, published=payload.published)
    return {"message":"created post", "data":new_post} 

#version 3
@app.get("/posts/{id}")
def fetch_one_post(id: int, db: Session = Depends(get_db)):

    orm_one_post = db.query(models.Post).filter(models.Post.id == id).first()
    print(orm_one_post)
    if not orm_one_post:    # if not success do this response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Post with id: {id} is not found')
    return {"your post details":orm_one_post}
    
#version 3
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    orm_query = db.query(models.Post).filter(models.Post.id == id)

    if orm_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    
    orm_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#version 3
@app.put("/posts/{id}")
def update_post(id: int, payload: Post, db: Session = Depends(get_db)):
    
    orm_query1 = db.query(models.Post).filter(models.Post.id == id)

    orm_updated_post = orm_query1.first()

    if orm_updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    
    orm_query1.update({'title':'new title'})

    return {"updated":orm_updated_post}

# version 3 - creating new path operation for orm testing
@app.get("/ormTest")   #path operation with http method
def fetch_new_1(db: Session = Depends(get_db)):
    orm_posts =  db.query(models.Post).all()
    return {"Post": orm_posts}

