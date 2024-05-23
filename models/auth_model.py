from pydantic import BaseModel


class AuthBase(BaseModel):
    account_token: str


class HistoryBase(BaseModel):
    account_token: str
    hoscode: str
    cid: str


class RegBase(BaseModel):
    account_token: str
    username: str
    password: str
    hoscode: str
    thaid_id: int
    datetime: str
    ip: str
    login_type: str


class ViewerBase(BaseModel):
    account_token: str
    hosCode: str
    cid: str
    patientCid: str
    patientHosCode: str
    ip: str


class LogBase(BaseModel):
    token: str
    hosCode: str
    cid: str
    patientCid: str
    patientHosCode: str
    datetime: str
    ip: str

