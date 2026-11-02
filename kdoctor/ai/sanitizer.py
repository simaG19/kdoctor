
import re


REDACTED = "[REDACTED]"

# Sensitive key names commonly found in DevOps environments.
SENSITIVE_KEY_PATTERN = re.compile(
    r"password|passwd|secret|token|api[_-]?key|"
    r"access[_-]?key|private[_-]?key|client[_-]?secret|"
    r"authorization|credential",
    re.IGNORECASE,
)

# Common sensitive values found in logs and configuration files.
SENSITIVE_VALUE_PATTERNS = [
    re.compile(
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"
    ),
       re.compile(
        r"""(?i)\b(password|passwd|token|api[_-]?key|client[_-]?secret)\s*[:=]\s*['"]?[^\s,;'" ]+"""
    ),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
        r".*?"
        r"-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
]


def sanitize_key_value(key, value):
    """Redact values whose configuration keys are sensitive."""

    if SENSITIVE_KEY_PATTERN.search(str(key)):
        return REDACTED

    if isinstance(value, dict):
        return sanitize_data(value)

    if isinstance(value, list):
        return [
            sanitize_key_value(key, item)
            for item in value
        ]

    if isinstance(value, str):
        return sanitize_text(value)

    return value


def sanitize_data(data):
    """Recursively sanitize dictionaries and lists."""

    if isinstance(data, dict):
        return {
            key: sanitize_key_value(key, value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [
            sanitize_data(item)
            for item in data
        ]

    if isinstance(data, str):
        return sanitize_text(data)

    return data


def sanitize_text(text):
    """Redact recognizable secrets from free-form text."""

    sanitized = text

    for pattern in SENSITIVE_VALUE_PATTERNS:
        sanitized = pattern.sub(REDACTED, sanitized)

    return sanitized
