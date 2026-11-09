from backend.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_authentication():

    password = "YuvaAI_Test_2026!"

    # Test password hashing.
    hashed = hash_password(password)

    assert hashed != password

    # Test correct password.
    assert verify_password(password, hashed)

    # Test incorrect password.
    assert not verify_password("WrongPassword123!", hashed)

    # Test JWT creation.
    token = create_access_token(1)

    assert isinstance(token, str)

    # Test JWT verification.
    user_id = decode_access_token(token)

    assert user_id == 1

    # Test invalid token.
    assert decode_access_token("invalid-token") is None

    print("All YuvaAI authentication tests passed!")


if __name__ == "__main__":
    test_authentication()