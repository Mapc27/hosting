from fastapi import FastAPI, Depends

from auth import auth, scheme
from auth.token import get_current_user

app = FastAPI()


app.include_router(auth.router)


@app.get("/")
def index(user: scheme.User = Depends(get_current_user)):
    return {"Hello": "World"}
