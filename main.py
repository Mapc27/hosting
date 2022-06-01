from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from auth import auth, scheme
from auth.token import get_current_user, SECRET_KEY
from chat import views as chat_views

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.include_router(auth.router)
app.include_router(chat_views.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index() -> dict:
    return {"Hello": "World"}
