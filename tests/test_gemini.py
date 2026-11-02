
from types import SimpleNamespace

import pytest

from kdoctor.ai import (
    GeminiClient,
    GeminiConfigurationError,
    GeminiRequestError,
)


class FakeModels:
    """Simulates the Gemini models API."""

    def __init__(self, response):
        self.response = response
        self.received_model = None
        self.received_prompt = None

    def generate_content(self, model, contents):
        self.received_model = model
        self.received_prompt = contents
        return self.response


class FakeGeminiClient:
    """Simulates the Google GenAI client."""

    def __init__(self, response):
        self.models = FakeModels(response)
        self.closed = False

    def close(self):
        self.closed = True


def test_gemini_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(
        GeminiConfigurationError,
        match="GEMINI_API_KEY",
    ):
        GeminiClient()


def test_generate_text_returns_response():
    fake_client = FakeGeminiClient(
        SimpleNamespace(text="The pod is failing because of memory limits.")
    )

    gemini = GeminiClient(
        client=fake_client,
        model="test-model",
    )

    result = gemini.generate_text("Diagnose this Kubernetes issue.")

    assert result == "The pod is failing because of memory limits."
    assert fake_client.models.received_model == "test-model"
    assert fake_client.models.received_prompt == (
        "Diagnose this Kubernetes issue."
    )


def test_generate_text_rejects_empty_prompt():
    fake_client = FakeGeminiClient(SimpleNamespace(text="Some response"))

    gemini = GeminiClient(client=fake_client)

    with pytest.raises(ValueError, match="prompt cannot be empty"):
        gemini.generate_text("   ")


def test_generate_text_rejects_empty_response():
    fake_client = FakeGeminiClient(SimpleNamespace(text="  "))

    gemini = GeminiClient(client=fake_client)

    with pytest.raises(
        GeminiRequestError,
        match="empty response",
    ):
        gemini.generate_text("Diagnose this issue.")


def test_close_releases_client():
    fake_client = FakeGeminiClient(SimpleNamespace(text="Response"))

    gemini = GeminiClient(client=fake_client)
    gemini.close()

    assert fake_client.closed is True
