from pydantic import BaseModel


class User(BaseModel):
    login: str
    email: str = None
    password: str = None
    cash: int = None
    verify: bool = False


class PasswordsChange(BaseModel):
    oldPassword: str
    newPassword: str


class Deposit(BaseModel):
    deposit: int


class VerifyRequest(BaseModel):
    code: int
    hashcode: str
    email: str


class GoodResponse(BaseModel):

    resultCode: int = 0

    def __init__(self, code, **data):
        super().__init__(**data)
        self.resultCode = code

# 100 - verify email sends
# 101 - verify success
# 102 - refresh tokens, send request again
# 103 - operation success


class BadResponse(BaseModel):

    resultCode: int = 1

    def __init__(self, code, **data):
        super().__init__(**data)
        self.resultCode = code

# 1 - login is not in db or login already register
# 2 - uncorrected password or email already register
# 3 - bad email
# 4 - uncorrected verify code
# 5 - old refresh token
# 66 - all bad

