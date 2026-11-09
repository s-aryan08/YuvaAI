"""
YuvaAI - Authentication Service Tests

Tests registration, login and duplicate email protection.
"""

from backend.database import SessionLocal

from backend.auth.auth_service import (
    register_user,
    authenticate_user,
    EmailAlreadyRegisteredError
)


def test_authentication_service():

    db = SessionLocal()

    test_email = "yuvaai.test@example.com"
    test_password = "YuvaAI_Test_2026!"
    test_name = "YuvaAI Test"

    try:

        # Clean up a previous test account.
        existing = (
            db.query(
                __import__(
                    "backend.models",
                    fromlist=["User"]
                ).User
            )
            .filter_by(email=test_email)
            .first()
        )

        if existing:
            db.delete(existing)
            db.commit()

        # 1. Test registration.

        user = register_user(
            db,
            test_name,
            test_email,
            test_password
        )

        assert user.id is not None
        assert user.email == test_email
        assert user.password_hash != test_password

        print("Registration: PASSED")

        # 2. Test login.

        authenticated_user = authenticate_user(
            db,
            test_email,
            test_password
        )

        assert authenticated_user.id == user.id

        print("Login: PASSED")

        # 3. Test wrong password.

        try:

            authenticate_user(
                db,
                test_email,
                "WrongPassword123!"
            )

            raise AssertionError(
                "Incorrect password was accepted."
            )

        except Exception as error:

            from backend.auth.auth_service import InvalidCredentialsError

            if not isinstance(error, InvalidCredentialsError):
                raise

        print("Incorrect password rejection: PASSED")

        # 4. Test duplicate email.

        try:

            register_user(
                db,
                test_name,
                test_email,
                test_password
            )

            raise AssertionError(
                "Duplicate registration was accepted."
            )

        except EmailAlreadyRegisteredError:
            pass

        print("Duplicate email protection: PASSED")

        print("\nAll YuvaAI authentication service tests passed!")

    finally:

        db.close()


if __name__ == "__main__":
    test_authentication_service()