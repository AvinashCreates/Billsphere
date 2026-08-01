import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient

from app.database.database import init_db
from main import app


class AuthRegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_register_creates_user(self):
        with TestClient(app) as client:
            response = client.post(
                "/auth/register",
                json={"email": "test@example.com", "password": "secret123", "role": "customer"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["email"], "test@example.com")


if __name__ == "__main__":
    unittest.main()
