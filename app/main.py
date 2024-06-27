# main app to be built here
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel  # for schema validation
from typing import Optional     # for optional field in schema
from random import randrange

# uvicorn main:app --reload     >> for running the fastApi app
#new >> we put main.py in a app folder(a pakage initiated with __init__.py)
# uvicorn app.main:app --reload

# for built-in documentation 
# http://127.0.0.1:8000/docs     >> for Swagger UI doc ready to share
# or
# http://127.0.0.1:8000/redoc     >> diff format

app = FastAPI()

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

class Post(BaseModel):
    title: str
    content: str                    #required
    published: bool = False         #default value >> optional field for the user 
#    rating: Optional[int]= None     

# the @ is a decorater
@app.get("/")   #path operation with http method
async def main_page():
    return {"Post": "Hello World>>>>>>"}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(payload: Post):
    print(payload)
    print(payload.model_dump())     # .dict()  >> changed to .model_dump() in Pydantic
    post_dict = payload.model_dump()
    post_dict['id'] = randrange(0,10000)
    my_posts.append(post_dict)
    return {"data":post_dict}   

@app.get("/posts")   #path operation with http method
def fetch_posts():
    return {"Post": my_posts}

@app.get("/posts/{id}")
def fetch_post(id: int):
    one_post = find_Post(id) #the path param is always a str convert to int
    print(one_post)
    if not one_post:    # if not success do this response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Post with id: {id} is not found')
    return {"your post details":one_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

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