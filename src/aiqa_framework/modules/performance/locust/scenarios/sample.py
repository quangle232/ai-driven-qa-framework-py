"""Sample Locust task set — browse the users API."""

from __future__ import annotations

from locust import TaskSet, task


class UserBrowsing(TaskSet):
    @task(3)
    def list_users(self) -> None:
        self.client.get("/users", name="GET /users")

    @task(1)
    def get_user(self) -> None:
        self.client.get("/users/u1", name="GET /users/:id")
