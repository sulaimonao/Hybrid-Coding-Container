"""Minimal session-based authentication utilities."""
from __future__ import annotations

from typing import Dict

from fastapi import HTTPException, Request, Response, status
from itsdangerous import BadSignature, URLSafeSerializer
from passlib.context import CryptContext

from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """Authenticate users and manage signed cookies."""

    def __init__(self) -> None:
        self.serializer = URLSafeSerializer(settings.session_secret_key, salt="uct-session")
        self._users: Dict[str, str] = {}
        self._bootstrap_default_user()

    def _bootstrap_default_user(self) -> None:
        hashed = pwd_context.hash(settings.admin_password)
        self._users[settings.admin_email] = hashed

    def authenticate(self, email: str, password: str) -> bool:
        hashed = self._users.get(email)
        if not hashed:
            return False
        return pwd_context.verify(password, hashed)

    def issue_session(self, response: Response, email: str) -> None:
        token = self.serializer.dumps({"email": email})
        response.set_cookie(
            key=settings.session_cookie_name,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
        )

    def clear_session(self, response: Response) -> None:
        response.delete_cookie(settings.session_cookie_name)

    def current_user(self, request: Request) -> str:
        token = request.cookies.get(settings.session_cookie_name)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        try:
            data = self.serializer.loads(token)
        except BadSignature as exc:  # noqa: PERF203
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc
        email = data.get("email")
        if not email or email not in self._users:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
        return email


auth_manager = AuthManager()


def require_user(request: Request) -> str:
    return auth_manager.current_user(request)


def login_user(email: str, password: str, response: Response) -> None:
    if not auth_manager.authenticate(email, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    auth_manager.issue_session(response, email)


def logout_user(response: Response) -> None:
    auth_manager.clear_session(response)
