"""Locust entry point — a sample HTTP user against the users API.

Interactive:
    uv run --with locust locust -f src/aiqa_framework/modules/performance/locust/locustfile.py \
      --host http://localhost:8000
Headless (CI/smoke):
    ... --headless -u 10 -r 2 -t 15s
"""

from __future__ import annotations

from locust import HttpUser, between

from aiqa_framework.modules.performance.locust.scenarios.sample import UserBrowsing


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)
    tasks = [UserBrowsing]
