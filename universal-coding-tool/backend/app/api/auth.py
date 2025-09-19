"""Authentication endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel, EmailStr

from ..core.auth import login_user, logout_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/auth/login")
async def login(payload: LoginRequest, response: Response) -> dict[str, str]:
    login_user(payload.email, payload.password, response)
    return {"email": payload.email}


@router.post("/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    logout_user(response)
    return {"status": "logged-out"}
