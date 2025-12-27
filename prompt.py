import os

from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()  # loads .env into os.environ

with OpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    response = client.chat.send(
        model="minimax/minimax-m2",
        messages=[
            {"role": "user", "content": "Explain quantum computing!"}
        ]
    )

    print(response.choices[0].message.content)
