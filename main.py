from fastapi import FastAPI

from auth import user

app = FastAPI()


app.include_router(user.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
