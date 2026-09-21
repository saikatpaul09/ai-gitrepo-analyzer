import os

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()


class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL")

        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY is not configured"
            )

        if not base_url:
            raise RuntimeError(
                "LLM_BASE_URL is not configured"
            )

        if not model:
            raise RuntimeError(
                "LLM_MODEL is not configured"
            )

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.model = model

    async def analyze(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""