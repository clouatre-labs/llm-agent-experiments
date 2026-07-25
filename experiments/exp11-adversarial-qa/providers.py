"""Model provider interface for the experiment.

Provides call_openrouter() and call_bedrock() with retry logic.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

import boto3
import botocore.exceptions
import openai

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    """Normalized result from a model call."""

    content: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    success: bool = True


def call_openrouter(
    prompt: str,
    system: str,
    model_id: str,
    config: dict[str, Any],
    max_retries: int = 3,
) -> ChatResult:
    """Call an OpenRouter model via the OpenAI SDK.

    Uses response_format=json_object when available.
    Retries on openai.RateLimitError.
    """
    client = openai.OpenAI(
        api_key=config.get("api_key"),
        base_url="https://openrouter.ai/api/v1",
    )
    messages = [{"role": "user", "content": prompt}]
    kwargs = {
        "model": model_id,
        "messages": messages,
        "max_tokens": config.get("max_tokens", 4096),
        "temperature": config.get("temperature", 0.5),
    }
    if config.get("json_mode", False):
        kwargs["response_format"] = {"type": "json_object"}

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            return ChatResult(
                content=choice.message.content or "",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                stop_reason=choice.finish_reason or "unknown",
            )
        except openai.RateLimitError as e:
            last_error = e
            wait = 2**attempt
            logger.warning(
                "Rate limited (attempt %d/%d), waiting %ds",
                attempt + 1,
                max_retries,
                wait,
            )
            time.sleep(wait)
        except openai.APIError as e:
            last_error = e
            wait = 2**attempt
            logger.warning(
                "API error (attempt %d/%d): %s, waiting %ds",
                attempt + 1,
                max_retries,
                e,
                wait,
            )
            time.sleep(wait)

    raise last_error  # type: ignore[misc]


def call_bedrock(
    prompt: str,
    system: str,
    model_id: str,
    config: dict[str, Any],
    max_retries: int = 3,
) -> ChatResult:
    """Call a Bedrock model via the AWS boto3 Converse API.

    System prompt is passed as a separate [{'text': ...}] parameter.
    Text is extracted from response['output']['message']['content'][0]['text'].
    Handles stopReason 'content_filtered' and 'max_tokens' as failures.
    Retries on botocore.exceptions.ClientError with throttling code.
    """
    client = boto3.Session().client("bedrock-runtime")

    system_param = [{"text": system}]
    inference_config = {
        "maxTokens": config.get("max_tokens", 4096),
        "temperature": config.get("temperature", 0.5),
    }
    messages = [{"role": "user", "content": [{"text": prompt}]}]

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.converse(
                modelId=model_id,
                messages=messages,
                system=system_param,
                inferenceConfig=inference_config,
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in (
                "ThrottlingException",
                "ProvisionedThroughputExceededException",
            ):
                last_error = e
                wait = 2**attempt
                logger.warning(
                    "Throttled (attempt %d/%d), waiting %ds",
                    attempt + 1,
                    max_retries,
                    wait,
                )
                time.sleep(wait)
                continue
            raise

        stop_reason = response.get("stopReason", "unknown")
        content_list = response.get("output", {}).get("message", {}).get("content", [])
        if not content_list:
            return ChatResult(
                content="",
                input_tokens=0,
                output_tokens=0,
                stop_reason=stop_reason or "empty_content",
                success=False,
            )

        text = content_list[0].get("text", "")

        if stop_reason in ("content_filtered", "max_tokens"):
            return ChatResult(
                content=text,
                input_tokens=response.get("usage", {}).get("inputTokens", 0),
                output_tokens=response.get("usage", {}).get("outputTokens", 0),
                stop_reason=stop_reason,
                success=False,
            )

        return ChatResult(
            content=text,
            input_tokens=response.get("usage", {}).get("inputTokens", 0),
            output_tokens=response.get("usage", {}).get("outputTokens", 0),
            stop_reason=stop_reason,
        )

    raise last_error  # type: ignore[misc]
