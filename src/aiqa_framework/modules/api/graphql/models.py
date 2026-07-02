"""GraphQL contract models — pydantic (validate the ``data`` payload)."""

from __future__ import annotations

from pydantic import BaseModel


class GqlUser(BaseModel):
    id: str
    username: str
    email: str


class UserData(BaseModel):
    user: GqlUser | None


class UsersData(BaseModel):
    users: list[GqlUser]
