import asyncio

from app.llm.client import OpenAIClient


async def main():

    client = OpenAIClient()

    response = await client.analyze(
        "Explain what a REST API is in one short paragraph."
    )

    print("\nLLM Response:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())