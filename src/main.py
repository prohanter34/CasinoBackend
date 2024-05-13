from fastapi import FastAPI, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from src.utils.JWT import JWTFabric
import uvicorn
from typing import Annotated
from starlette.responses import JSONResponse
import hashlib
from src.database.database import Database
from src.schemas.schemas import User, GoodResponse, BadResponse, VerifyRequest
from src.utils.utils import generate_verify_code, send_register_email, get_hash

app = FastAPI()
print('start')

path = 'localhost'
if 'MY_PATH' in os.environ:
    path = os.environ["MY_PATH"]

URL = os.getenv("DB_URL")
database = Database(URL)
secret = os.getenv("JWT_SECRET")
JWTfabric = JWTFabric(secret)


@app.post("/auth/login")
def login(user: User):
    dbUser = database.get_user(user.login)
    if not dbUser:
        return BadResponse(1)
    else:
        if user.password == dbUser.password:
            return {
                'login': dbUser.login,
                'email': dbUser.email,
                'verify': dbUser.verify,
                'cash': dbUser.cash,
                'resultCode': 1000
            }
        else:
            return BadResponse(2)


@app.get("/auth")
def auth(request: Request):
    access_token = request.cookies.get("access_token")
    checked_access = JWTfabric.check_token(access_token)
    if checked_access.check_signature == checked_access.signature:
        user = database.get_user(checked_access.payload['login'])
        return user.to_schema()
    else:
        refresh_token = request.cookies.get("refresh_token")
        checked_refresh = JWTfabric.check_token(refresh_token)
        if checked_refresh.check_signature == checked_refresh.signature:
            # two week refresh token
            new_refresh = JWTfabric.generate_token(checked_refresh.payload["id"], checked_refresh.payload["login"], 60 * 24 * 14)
            new_access = JWTfabric.generate_token(checked_refresh.payload["id"], checked_refresh.payload["login"], 15)
            # TODO something wrong
            return add_cookie(GoodResponse(102), new_refresh, new_access)
        else:
            return BadResponse(5)


@app.post("/auth/registration")
def registration(user: User):
    if database.get_user(user.login) is not None:
        return BadResponse(1)
    elif not database.check_email(user.email):
        return BadResponse(2)
    else:
        verifyCode = generate_verify_code()
        result = send_register_email(message=verifyCode, receiver=user.email)
        if result == 0:
            database.add_user(login=user.login, email=user.email, password=user.password)
            hashcode = get_hash(str(verifyCode) + user.email)
            return {
                'hash': hashcode,
                'resultCode': 100
            }
        else:
            return BadResponse(3)


@app.post("/auth/registration/verify")
def verify_registration(request: VerifyRequest):
    hashcode = get_hash(str(request.code) + request.email)
    a1 = get_hash(str(request.code) + request.email)
    if hashcode == request.hashcode:
        database.verify_email(request.email)
        return GoodResponse(101)
    else:
        return BadResponse(4)


def add_cookie(content, refresh, access):
    response = JSONResponse(content=content)
    response.set_cookie(key="access_token", value=access)
    response.set_cookie(key="refresh_token", value=refresh)
    return response


origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app")