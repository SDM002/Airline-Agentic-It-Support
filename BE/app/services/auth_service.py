"""Login: checks the password hash in MongoDB and issues a JWT access token."""

from datetime import timedelta

import jwt
from pwdlib import PasswordHash

from app.config.settings import settings
from app.db.mongo import now, users
from app.services import employee_service

password_hash = PasswordHash.recommended()


async def authenticate(employee_id: str, password: str) -> dict | None:
    user = await users.find_one({"_id": employee_id})
    if user is None or not password_hash.verify(password, user.get("password_hash", "")):
        return None
    return await employee_service.get_employee(employee_id)


def create_access_token(employee_id: str, role: str) -> str:
    claims = {"sub": employee_id, "role": role, "exp": now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
    return jwt.encode(claims, settings.JWT_SECRET.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def read_access_token(token: str) -> str:
    """Returns the employee ID from a valid token; raises jwt.InvalidTokenError otherwise."""
    claims = jwt.decode(token, settings.JWT_SECRET.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
    return claims["sub"]
