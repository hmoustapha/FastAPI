import time
from fastapi import FastAPI, Response, status, HTTPException , Depends # Depend v3
from fastapi.params import Body
from pydantic import BaseModel, ConfigDict  # for schema validation 
from typing import Optional     # for optional field in schema
from random import randrange


# uvicorn Webhooks.TestWebhook:app --reload     >> for running the fastApi app
#new >> we put main.py in a app folder(a pakage initiated with __init__.py)
# uvicorn app.main:app --reload


app = FastAPI()
#app.config["PREFERRED_URL_SCHEME"] = "https"

# version 1
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

# version 1
class Post(BaseModel):  # for schema validation
    model_config = ConfigDict(extra='allow')   # forbid extra fields from user
    id: int = randrange(1,1000)
    content: Optional[str] = None
           #default value >> optional field for the user 
#    rating: Optional[int]= None     


# version 1 - the @ is a decorater
@app.get("/")   #path operation with http method
async def main_page():
    return {"Post": "Hello World>>>>>>"}

# version 1
@app.get("/posts")   #path operation with http method
def fetch_posts():
    return {"Post": my_posts}


# version 1
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(payload: Post):
    print(payload)
    print(payload.model_dump())     # .dict()  >> changed to .model_dump() in Pydantic
    post_dict = payload.model_dump()
    post_dict['id'] = randrange(0,10000)
    my_posts.append(post_dict)
    return Response(status_code=status.HTTP_200_OK)   

# version 1
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} not exist')
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
