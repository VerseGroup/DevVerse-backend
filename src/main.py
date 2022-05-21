# python imports
from fastapi import FastAPI, Request
from urllib import request
from src.requests import *
import uuid
import json
import os

# internal imports
from src.relay.relay import relay
from src.phone_numbers import NUMBERS
from src.twilio import sendMessage
from src.parse_webhook import parse_check_run

#postgres server
from src.postgres.models import User, Task, TodoList
from src.postgres.crud import Backend_Interface

# startup
app = FastAPI()
interface = Backend_Interface()


####### ROUTES [Basic] #######


@app.get("/ping", status_code=200)
async def ping():
    return {"message": "pong"} 


####### ROUTES [MAIN] #######


@app.post("/relay", status_code=200)
async def _relay(request: RelayRequest):
    try:
        response = relay(request)
        return {"message": "success", "response": response}
    except Exception as e:
        return {"message": "error", "exception" : str(e)}

@app.post("/adduser", status_code=200)
async def adduser(request: AddUserRequest):
    # add user to database
    return {"message": "user added"}
 
# post github data (testing)
@app.post("/data", status_code=200)
async def scrape_(request: OauthPostRequest):
    return request

# recieve data from github
@app.post("/webhook", status_code=200)
async def webhook(request: Request):
    
    _json = json.load(request.json())

    # univeral data
    repo = _json['repository']['name']
    
    if 'check_suite' in _json:
        body = parse_check_run(_json)

    if body is not None:        
        for number in NUMBERS:
            sendMessage(body, number)

@app.post("/addUser", status_code=200)
async def addUser(request: AddUserRequest):
    # add user to database
    user = User(request.username, request.email, request.password, request.phone, request.display_name, request.github_oauth_token)
    interface.create_user(user)
    return {"message": "user added"}

