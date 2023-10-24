from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from routers import auth_router

config_env = dotenv_values(".env")

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(auth_router.router2)
app.include_router(auth_router.router3)
