from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["authentication"])


@router.get("/login")
def read_root():
    return {"it": "login"}
