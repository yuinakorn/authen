from pydantic import BaseModel


class AuthBase(BaseModel):
    account_token: str


class RegBase(BaseModel):
    account_token: str
    username: str
    password: str


class ViewerBase(BaseModel):
    account_token: str
    hosCode: str
    cid: str
    patientCid: str
    patientHosCode: str
