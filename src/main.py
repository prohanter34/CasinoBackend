from fastapi import FastAPI, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from src.utils.JWT import JWTFabric
import uvicorn
from typing import Annotated
from starlette.responses import JSONResponse
import hashlib
from src.database.database import Database
from src.schemas.schemas import User, GoodResponse, BadResponse, VerifyRequest, Deposit, PasswordsChange
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
            content = {
                'login': dbUser.login,
                'email': dbUser.email,
                'verify': dbUser.verify,
                'cash': dbUser.cash,
                'resultCode': 1000
            }
            access = JWTfabric.generate_token(dbUser.id, dbUser.login, 15)
            refresh = JWTfabric.generate_token(dbUser.id, dbUser.login, 60 * 24 * 14)
            response = add_cookie(content, refresh, access)
            return response
        else:
            return BadResponse(2)


@app.post("/auth/changePass")
def change_password(data: PasswordsChange, access_token: str = Cookie(None)):
    login = check_token(access_token)
    if login is not None:
        user = database.get_user(login)
        if user.password == data.oldPassword:
            user.password = data.newPassword
            return GoodResponse(103)
        else:
            return BadResponse(2)
    else:
        return BadResponse(5)


@app.get("/auth")
def auth(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token is not None and access_token != "":
        checked_access = JWTfabric.check_token(access_token)
        if checked_access.is_valid():
            user = database.get_user(checked_access.payload['login'])
            return user.to_schema()
        else:
            refresh_token = request.cookies.get("refresh_token")
            checked_refresh = JWTfabric.check_token(refresh_token)
            if checked_refresh.is_valid():
                # two week refresh token
                new_refresh = JWTfabric.generate_token(checked_refresh.payload["id"], checked_refresh.payload["login"],
                                                       60 * 24 * 14)
                new_access = JWTfabric.generate_token(checked_refresh.payload["id"], checked_refresh.payload["login"],
                                                      15)
                user = database.get_user(checked_access.payload['login'])
                user = {
                    "login": user.login,
                    "email": user.email,
                    "verify": user.verify,
                    "cash": user.cash
                }
                return add_cookie(user, new_refresh, new_access)
            else:
                return BadResponse(5)
    else:
        return BadResponse(5)


@app.delete("/auth/logout")
def logout():
    response = add_cookie({"resultCode": 0}, "", "")
    return response


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


@app.post("/cash/deposit")
def deposit(deposit: Deposit, access_token: str = Cookie(None)):
    login = check_token(access_token)
    if login is not None:
        if database.change_user_cash(login, deposit.deposit):
            return GoodResponse(103)
        else:
            return BadResponse(66)
    else:
        return BadResponse(5)


def add_cookie(content, refresh, access):
    response = JSONResponse(content=content)
    response.set_cookie(key="access_token", value=access)
    response.set_cookie(key="refresh_token", value=refresh)
    return response


def check_tokens_of_request(request: Request):
    access = request.cookies.get("access_token")
    access_token = JWTfabric.check_token(access)
    if access_token.is_valid():
        return access_token.payload["login"]
    else:
        refresh = request.cookies.get("refresh_token")
        refresh_token = JWTfabric.check_token(refresh)
        if refresh_token.is_valid():
            # todo хз что делать в таком случае
            pass
        else:
            return None


def check_token(token: str):
    access_token = JWTfabric.check_token(token)
    if access_token.is_valid():
        return access_token.payload["login"]
    else:
        return None


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
