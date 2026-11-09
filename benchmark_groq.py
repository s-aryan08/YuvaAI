"""
YuvaAI - Advanced Groq Network Diagnostics

Measures:
- TCP connection time
- TLS handshake time
- Request transmission
- Response headers
- Response body
- Total HTTP request time
"""

import os
import time
import httpx

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")


URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

PAYLOAD = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Reply with exactly one word: Hello."
        }
    ],
    "max_completion_tokens": 30,
    "reasoning_effort": "low",
    "include_reasoning": False
}


events = []


def trace_callback(event_name, info):

    events.append({
        "time": time.perf_counter(),
        "event": event_name
    })


def main():

    print("\n========== YUVAAI NETWORK DIAGNOSTICS ==========")

    print(f"Model: {MODEL}")

    print("\nStarting HTTP request...\n")

    start_time = time.perf_counter()

    try:

        with httpx.Client(
            timeout=httpx.Timeout(60.0, connect=20.0),
            trust_env=False
        ) as client:

            response = client.post(
                URL,
                headers=HEADERS,
                json=PAYLOAD,
                extensions={
                    "trace": trace_callback
                }
            )

        total_time = time.perf_counter() - start_time

        print("\nHTTP STATUS:", response.status_code)

        print(f"TOTAL CLIENT TIME: {total_time:.3f}s")

        print("\n========== CONNECTION TRACE ==========")

        for event in events:

            elapsed = event["time"] - start_time

            print(
                f"{elapsed:.3f}s | {event['event']}"
            )

        print("\n========== GROQ METRICS ==========")

        if response.is_success:

            data = response.json()

            usage = data.get("usage", {})

            for metric in (
                "queue_time",
                "prompt_time",
                "completion_time",
                "total_time"
            ):

                value = usage.get(metric)

                if value is not None:

                    print(f"{metric}: {value:.4f}s")

            print("\nAI RESPONSE:")

            print(
                data["choices"][0]["message"]["content"]
            )

        else:

            print("API ERROR:", response.text[:500])

    except Exception as error:

        print(
            f"\nDIAGNOSTIC ERROR: "
            f"{type(error).__name__}: {error}"
        )

    print("\n========== DIAGNOSTIC COMPLETE ==========\n")


if __name__ == "__main__":
    main()