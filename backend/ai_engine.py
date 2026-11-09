"""
YuvaAI - AI Engine

Handles communication between YuvaAI and Groq API.
Supports normal and streaming AI responses.

Includes performance monitoring and latency diagnostics.
"""

import time

from typing import Optional

import httpx

from groq import Groq, DefaultHttpxClient

from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    validate_settings
)


# ==========================================
# 1. INITIALIZE AI CLIENT
# ==========================================

validate_settings()

client = Groq(
    api_key=GROQ_API_KEY,
    timeout=30.0,
    max_retries=0,

    http_client=DefaultHttpxClient(
        transport=httpx.HTTPTransport(
            local_address="0.0.0.0"
        )
    )
)


# ==========================================
# 2. SYSTEM INSTRUCTIONS
# ==========================================

SYSTEM_PROMPT = """
You are YuvaAI, a helpful and intelligent AI assistant.

Answer accurately, clearly, and naturally.

Help users with:
- Learning and education
- Programming and technology
- Problem solving
- Writing and creativity
- General questions

Keep simple answers concise.
Give detailed explanations when needed.
Use examples when they improve understanding.
Be honest when uncertain.
"""


# ==========================================
# 3. PREPARE CONVERSATION MESSAGES
# ==========================================

def prepare_messages(
    message: str,
    history: Optional[list] = None
) -> list:

    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    if history is None:
        history = []

    # Keep only the latest 10 messages.
    recent_history = history[-10:]

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(recent_history)

    messages.append({
        "role": "user",
        "content": message.strip()
    })

    return messages


# ==========================================
# 4. GROQ PERFORMANCE DIAGNOSTICS
# ==========================================

def log_server_metrics(completion, client_time: float):

    print("\n========== YuvaAI PERFORMANCE ==========")

    print(f"Model: {GROQ_MODEL}")

    print(
        f"Client response time: {client_time:.3f}s"
    )

    usage = getattr(completion, "usage", None)

    if usage:

        metric_names = [
            "queue_time",
            "prompt_time",
            "completion_time",
            "total_time"
        ]

        print("\nGroq Server Metrics:")

        for metric_name in metric_names:

            value = getattr(
                usage,
                metric_name,
                None
            )

            if value is not None:

                print(
                    f"{metric_name}: {value:.4f}s"
                )

        prompt_tokens = getattr(
            usage,
            "prompt_tokens",
            0
        )

        completion_tokens = getattr(
            usage,
            "completion_tokens",
            0
        )

        print("\nToken Usage:")

        print(f"Prompt tokens: {prompt_tokens}")

        print(f"Completion tokens: {completion_tokens}")

        completion_time = getattr(
            usage,
            "completion_time",
            None
        )

        if completion_time and completion_time > 0:

            tokens_per_second = (
                completion_tokens / completion_time
            )

            print(
                f"Generation speed: {tokens_per_second:.2f} tokens/sec"
            )

    else:

        print(
            "Groq server-side usage metrics unavailable."
        )

    # Groq request identifier.
    x_groq = getattr(completion, "x_groq", None)

    request_id = getattr(
        x_groq,
        "id",
        None
    )

    if request_id:

        print(f"Groq Request ID: {request_id}")

    print("========================================\n")


# ==========================================
# 5. NORMAL AI RESPONSE
# ==========================================

def generate_response(
    message: str,
    history: Optional[list] = None
) -> str:

    messages = prepare_messages(
        message,
        history
    )

    try:

        start_time = time.perf_counter()

        completion = client.chat.completions.create(

            model=GROQ_MODEL,

            messages=messages,

            temperature=0.4,

            max_completion_tokens=400,

            reasoning_effort="low",

            include_reasoning=False
        )

        elapsed_time = (
            time.perf_counter() - start_time
        )

        response = (
            completion.choices[0].message.content
        )

        if not response or not response.strip():

            raise RuntimeError(
                "The AI returned an empty response."
            )

        # Print performance diagnostics.
        log_server_metrics(
            completion,
            elapsed_time
        )

        return response.strip()

    except Exception as error:

        print(
            f"\n[YuvaAI] AI Engine Error: {error}"
        )

        raise RuntimeError(
            "Unable to generate an AI response."
        ) from error


# ==========================================
# 6. STREAMING AI RESPONSE
# ==========================================

def stream_response(
    message: str,
    history: Optional[list] = None
):

    messages = prepare_messages(
        message,
        history
    )

    start_time = time.perf_counter()

    first_token_time = None

    generated_text = ""

    try:

        stream = client.chat.completions.create(

            model=GROQ_MODEL,

            messages=messages,

            temperature=0.4,

            max_completion_tokens=400,

            reasoning_effort="low",

            include_reasoning=False,

            stream=True
        )

        # Receive AI-generated chunks.
        for chunk in stream:

            if not chunk.choices:
                continue

            content = (
                chunk.choices[0].delta.content
            )

            if content:

                # Measure time until first generated text.
                if first_token_time is None:

                    first_token_time = (
                        time.perf_counter() - start_time
                    )

                generated_text += content

                # Send chunk immediately.
                yield content

        elapsed_time = (
            time.perf_counter() - start_time
        )

        if not generated_text:

            raise RuntimeError(
                "The AI returned an empty response."
            )

        print("\n========== YuvaAI STREAMING ==========")

        print(f"Model: {GROQ_MODEL}")

        if first_token_time is not None:

            print(
                f"Time to first token: {first_token_time:.3f}s"
            )

        print(
            f"Total streaming time: {elapsed_time:.3f}s"
        )

        print("======================================\n")

    except Exception as error:

        print(
            f"\n[YuvaAI] Streaming Error: {error}"
        )

        raise RuntimeError(
            "Unable to generate a streaming AI response."
        ) from error