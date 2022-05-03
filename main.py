from fastapi import FastAPI, Depends

from auth import auth, scheme
from auth.token import get_current_user
from chat import views as chat_views

app = FastAPI()


app.include_router(auth.router)
app.include_router(chat_views.router)


@app.get("/")
def index() -> dict:
    return {"Hello": "World"}
