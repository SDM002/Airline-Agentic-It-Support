from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import current_user
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # form.username is the employee ID, e.g. EMP001 or IT001
    user = await auth_service.authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect employee ID or password")
    token = auth_service.create_access_token(user["id"], user["role"])
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me")
async def me(user: dict = Depends(current_user)):
    return user
