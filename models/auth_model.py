from pydantic import BaseModel


class AuthBase(BaseModel):
    account_token: str

