from pydantic import BaseModel


class AuthBase(BaseModel):
    account_token: str


class RegBase(BaseModel):
    account_token: str
    username: str
    password: str
    hoscode: str
    thaid_id: int
    datetime: str
    ip: str


class ViewerBase(BaseModel):
    account_token: str
    hosCode: str
    cid: str
    patientCid: str
    patientHosCode: str


class LogBase(BaseModel):
    account_token: str
    hosCode: str
    cid: str
    patientCid: str
    patientHosCode: str
    datetime: str
    ip: str

