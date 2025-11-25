"""Ollama LLM provider for local model inference."""

import time
from typing import Optional

import requests

from ..config.config_loader import load_config
from ..utils.exceptions import APIError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OllamaProvider:
    """Provider for Ollama local LLM models."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., 'gemma3:1b'). If None, uses config default.
            base_url: Ollama API endpoint
            temperature: Sampling temperature (0-1). If None, uses config default.
            max_tokens: Maximum tokens to generate. If None, uses config default.
        """
        self.config = load_config()
        self.base_url = base_url
        self.model = model or self.config.llm.models.primary
        self.temperature = temperature if temperature is not None else self.config.llm.temperature
        self.max_tokens = max_tokens if max_tokens is not None else self.config.llm.max_tokens

        # Validate parameters
        if not (0 <= self.temperature <= 1):
            raise ValueError(f"Temperature must be 0-1, got {self.temperature}")
        if self.max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")

        # Verify Ollama is running and model is available
        self._verify_connection()

        logger.info(f"Ollama provider initialized with model: {self.model}")

    def _verify_connection(self):
        """Verify connection to Ollama and check if model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()

            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Check if our model is available
            if not any(self.model in name for name in model_names):
                logger.warning(
                    f"Model '{self.model}' not found in Ollama. "
                    f"Available models: {', '.join(model_names)}"
                )
                logger.warning(
                    f"You may need to run: ollama pull {self.model}"
                )
            else:
                logger.info(f"✓ Model '{self.model}' is available")

        except requests.exceptions.RequestException as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {str(e)}")
            logger.error("Make sure Ollama is running. Try: ollama serve")
            raise RuntimeError(f"Ollama connection failed: {str(e)}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Generate text using Ollama.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stream: Whether to stream the response (not implemented yet)

        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Build the request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temp,
                "num_predict": max_tok,
            },
            "stream": False
        }

        max_retries = getattr(self.config.llm, 'retries', 3)

        for attempt in range(max_retries):
            try:
                logger.debug(f"Generating (attempt {attempt + 1}/{max_retries}), prompt length: {len(prompt)} chars")

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.config.llm.timeout_seconds
                )
                response.raise_for_status()

                result = response.json()
                generated_text = result.get("response", "")

                logger.debug(f"Generated {len(generated_text)} chars")
                return generated_text.strip()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Request timed out, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Ollama request timed out after {max_retries} attempts")
                    raise APIError("LLM generation timed out after all retries")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {str(e)}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Ollama API error after {max_retries} attempts: {str(e)}")
                    raise APIError(f"LLM generation failed: {str(e)}")

    def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Chat completion using Ollama's chat endpoint.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated response
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temp,
                "num_predict": max_tok,
            },
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.llm.timeout_seconds
            )
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "").strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama chat API error: {str(e)}")
            raise RuntimeError(f"Chat generation failed: {str(e)}")
