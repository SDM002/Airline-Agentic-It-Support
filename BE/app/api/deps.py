"""Shared FastAPI dependencies: who is calling, and are they allowed."""

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services import auth_service, employee_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        employee_id = auth_service.read_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user = await employee_service.get_employee(employee_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def require_roles(*roles: str):
    async def check(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail=f"Requires role: {', '.join(roles)}")
        return user

    return check
