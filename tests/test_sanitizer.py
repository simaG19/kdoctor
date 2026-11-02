
from kdoctor.ai.sanitizer import (
    REDACTED,
    sanitize_data,
    sanitize_text,
)


def test_sanitize_sensitive_dictionary_values():
    data = {
        "pod": "backend-api",
        "password": "my-password",
        "api_key": "my-api-key",
        "namespace": "production",
    }

    result = sanitize_data(data)

    assert result["pod"] == "backend-api"
    assert result["namespace"] == "production"
    assert result["password"] == REDACTED
    assert result["api_key"] == REDACTED


def test_sanitize_nested_dictionary():
    data = {
        "application": {
            "name": "backend",
            "database": {
                "username": "admin",
                "password": "db-password",
            },
        }
    }

    result = sanitize_data(data)

    assert result["application"]["name"] == "backend"
    assert result["application"]["database"]["username"] == "admin"
    assert result["application"]["database"]["password"] == REDACTED


def test_sanitize_list_of_dictionaries():
    data = [
        {"name": "frontend", "token": "frontend-token"},
        {"name": "backend", "token": "backend-token"},
    ]

    result = sanitize_data(data)

    assert result[0]["name"] == "frontend"
    assert result[0]["token"] == REDACTED
    assert result[1]["token"] == REDACTED


def test_sanitize_bearer_token():
    text = "Authorization: Bearer abc123secret"

    result = sanitize_text(text)

    assert "abc123secret" not in result
    assert REDACTED in result


def test_sanitize_password_in_text():
    text = "password=my-secret-password"

    result = sanitize_text(text)

    assert "my-secret-password" not in result
    assert REDACTED in result


def test_sanitize_private_key():
    private_key = (
        "-----BEGIN PRIVATE KEY-----\n"
        "super-secret-private-key-content\n"
        "-----END PRIVATE KEY-----"
    )

    result = sanitize_text(private_key)

    assert "super-secret-private-key-content" not in result
    assert REDACTED in result


def test_preserve_non_sensitive_values():
    data = {
        "pod": "backend-api",
        "namespace": "production",
        "replicas": 3,
        "ready": True,
    }

    result = sanitize_data(data)

    assert result == data
