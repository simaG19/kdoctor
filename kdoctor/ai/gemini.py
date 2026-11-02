
import os

from google import genai
from google.genai import errors


DEFAULT_MODEL = "gemini-3.8-flash"


class GeminiConfigurationError(ValueError):
    """Raised when Gemini is not configured correctly."""


class GeminiRequestError(RuntimeError):
    """Raised when a Gemini API request fails."""


class GeminiClient:
    """Small wrapper around the Google Gemini API."""

    def __init__(self, api_key=None, model=None, client=None):
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")

        if client is None and not resolved_api_key:
            raise GeminiConfigurationError(
                "Gemini API key not found. "
                "Set the GEMINI_API_KEY environment variable."
            )

        self.model = (
            model
            or os.getenv("KDOCTOR_GEMINI_MODEL")
            or DEFAULT_MODEL
        )

        self._client = client or genai.Client(api_key=resolved_api_key)

    def generate_text(self, prompt):
        """Send a text prompt to Gemini and return its response."""

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("The prompt cannot be empty.")

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt
            )
        except errors.APIError as exc:
            raise GeminiRequestError(
                f"Gemini API request failed "
                f"(HTTP {exc.code}): {exc.message}"
            ) from exc

        response_text = response.text

        if not response_text or not response_text.strip():
            raise GeminiRequestError(
                "Gemini returned an empty response."
            )

        return response_text.strip()

    def close(self):
        """Release the underlying HTTP client resources."""

        close_method = getattr(self._client, "close", None)

        if callable(close_method):
            close_method()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
