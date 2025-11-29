import json
from typing import Dict
import boto3


def get_bedrock_client(region_name: str = "us-east-1"):
    """Returns a Bedrock Runtime client (assumes AWS creds are configured)."""
    return boto3.client("bedrock-runtime", region_name=region_name)


def call_bedrock_claude(prompt: str, max_tokens: int = 4000) -> str:
    """Calls Claude 3.5 Sonnet on Amazon Bedrock with a single user prompt."""
    client = get_bedrock_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(body),
    )

    raw_body = response["body"].read()
    data = json.loads(raw_body)
    parts = data.get("content", [])
    text_chunks = []
    for part in parts:
        if part.get("type") == "text":
            text_chunks.append(part.get("text", ""))
    return "".join(text_chunks)


if __name__ == "__main__":
    print(call_bedrock_claude("Say hello in one short sentence."))