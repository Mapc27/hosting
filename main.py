from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from auth.auth import router as auth_router
from auth.token import SECRET_KEY
from core.views import router as core_router
from chat.views import router as chat_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.include_router(auth_router)
app.include_router(core_router)
app.include_router(chat_router)

origins = [
    "*",
    "http://localhost:3000",
    "https://accounts.google.com/.well-known/openid-configuration",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index() -> dict:
    return {"Hello": "World"}


app.mount("/media", StaticFiles(directory="media"), name="media")
