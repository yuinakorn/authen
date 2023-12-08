from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from routers import auth_router

# allow CORS origin
from fastapi.middleware.cors import CORSMiddleware

config_env = dotenv_values(".env")

app = FastAPI()

origins = [
    config_env["CORS_ORIGIN1"],
    config_env["CORS_ORIGIN2"],
    config_env["CORS_ORIGIN3"]
]

print(origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(auth_router.router2)
app.include_router(auth_router.router3)
