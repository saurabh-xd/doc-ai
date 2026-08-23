"""Fast offline checks for password and JWT helpers."""

import unittest
from unittest.mock import patch

import jwt

from app.core.auth import create_access_token
from app.core.security import hash_password, verify_password


class AuthTests(unittest.TestCase):
    def test_password_hashing(self):
        password_hash = hash_password("safe-password")
        self.assertTrue(verify_password("safe-password", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_access_token_contains_user_id(self):
        with patch("app.core.auth.JWT_SECRET", "a" * 32):
            token = create_access_token("user-123")
            payload = jwt.decode(token, "a" * 32, algorithms=["HS256"])

        self.assertEqual(payload["sub"], "user-123")
