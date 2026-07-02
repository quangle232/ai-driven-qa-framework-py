"""API contract models — pydantic (the zod analogue). Types double as runtime
validators; responses are validated against them so contract drift fails loudly.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, TypeAdapter, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str) -> str:
    if not _EMAIL_RE.match(value):
        raise ValueError("invalid email address")
    return value


class User(BaseModel):
    id: str
    username: str
    email: str
    createdAt: str  # ISO-8601

    _v_email = field_validator("email")(_validate_email)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: str

    _v_email = field_validator("email")(_validate_email)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User


class ErrorResponse(BaseModel):
    error: str
    message: str


#: For validating list responses (`UserList.validate_python(data)`).
UserList = TypeAdapter(list[User])
