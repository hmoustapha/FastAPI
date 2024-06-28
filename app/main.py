# main app to be built here
import time
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel, ConfigDict  # for schema validation 
from typing import Optional     # for optional field in schema
from random import randrange
import psycopg as db            # for connecting to postgres
from psycopg.rows import dict_row   # for matching rows in cursor

# uvicorn app.main:app --reload     >> for running the fastApi app
#new >> we put main.py in a app folder(a pakage initiated with __init__.py)
# uvicorn app.main:app --reload

# for built-in documentation 
# http://127.0.0.1:8000/docs     >> for Swagger UI doc ready to share
# or
# http://127.0.0.1:8000/redoc     >> diff format

app = FastAPI()

"""
# old version
# data stored in code to be given when post request comes
my_posts=[
    {"title":"Amazing stuff","Content":"Beaches Islands Rockets","published":False,"id":1},
    {"title":"Bad Stuff","Content":"Pollution Deforestation","published":True,"id":2}]

def find_Post(id):  #how doing search on single data from a list based on path param
    for p in my_posts:
        if p["id"] == id:
            return p

def find_post_index(id):
    for i,p in enumerate(my_posts): #enumerate helps find the index of a element
        if p["id"] == id:
            return i
"""

class Post(BaseModel):  # for schema validation
    model_config = ConfigDict(extra='forbid')   # forbid extra fields from user
    title: str
    content: str                    #required
    published: bool = False         #default value >> optional field for the user 
#    rating: Optional[int]= None     

# Setting up the database connection
while True:
    try:
        conn = db.connect(host='localhost', dbname='fastapi', 
                     user='postgres', password='@gres2010zero', 
                     row_factory=dict_row)
        cur = conn.cursor()
        print('database connected')
        break
    except db.Error as e:
        print("Connection failed. Retrying in 5 seconds...")
        print(f"Error: {e}")
        time.sleep(5)

# the @ is a decorater
@app.get("/")   #path operation with http method
async def main_page():
    return {"Post": "Hello World>>>>>>"}

"""
# old version
@app.get("/posts")   #path operation with http method
def fetch_posts():
    return {"Post": my_posts}
"""
@app.get("/posts")   #path operation with http method
def fetch_posts():
    cur.execute("""SELECT * FROM posts""")  # SQL query
    db_posts = cur.fetchall()
    return {"Post": db_posts}

"""
# old version
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(payload: Post):
    print(payload)
    print(payload.model_dump())     # .dict()  >> changed to .model_dump() in Pydantic
    post_dict = payload.model_dump()
    post_dict['id'] = randrange(0,10000)
    my_posts.append(post_dict)
    return {"data":post_dict}   
"""
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(payload: Post): #Post === BaseModel is a pydantic class
    cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                (payload.title, payload.content, payload.published))
                # usuing %s is a way to pass variable to sql query
                # essential for security
                # RETURNING for fetching added data from db
    db_new_post = cur.fetchone()
    conn.commit()   # commit the changes to db
    return {"message":"created post", "data":db_new_post}  

"""
#old version
@app.get("/posts/{id}")
def fetch_one_post(id: int):
    one_post = find_Post(id) #the path param is always a str convert to int
    print(one_post)
    if not one_post:    # if not success do this response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Post with id: {id} is not found')
    return {"your post details":one_post}
"""

@app.get("/posts/{id}")
def fetch_one_post(id: int):
    cur.execute("""SELECT * FROM posts WHERE id = %(id)s;""", {'id':id})  # SQL query another way
    #cur.execute("""SELECT * FROM posts WHERE id = %s;""", (str(id),))
    db_post = cur.fetchone()
    print(db_post)
    if not db_post:    # if not success do this response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Post with id: {id} is not found')
    return {"your post details":db_post}

"""
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
"""

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cur.execute("""DELETE FROM posts WHERE id = %(id)s RETURNING *""", {'id':str(id)})
    db_deleted_post = cur.fetchone()
    conn.commit()
    if db_deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    return {'message':'deleted post', 'data':db_deleted_post}

"""
# old version
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"updated":post_dict}
"""

@app.put("/posts/{id}")
def update_post(id: int, payload: Post):
    cur.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
                (payload.title, payload.content, payload.published, str(id)))
    db_updated_post = cur.fetchone()
    conn.commit()
    if db_updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    return {"updated":db_updated_post}