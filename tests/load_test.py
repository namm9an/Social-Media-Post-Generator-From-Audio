"""Locust load-test script for production deployments.

Run with:
    locust -f tests/load_test.py --host=https://yourdomain.com
"""
from locust import HttpUser, task, between


class APILoadUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def basic_health(self):
        self.client.get("/api/health")

    @task(2)
    def metrics(self):
        self.client.get("/api/metrics")

    @task
    def upload_health(self):
        self.client.get("/api/health/storage")
