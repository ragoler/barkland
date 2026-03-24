import asyncio
import os
from google import genai
from google.genai import types
from pydantic import BaseModel

class BarkOutput(BaseModel):
    bark: str
    translation: str

async def main():
    if not os.environ.get("GEMINI_API_KEY"):
         print("GEMINI_API_KEY not set")
         return
    
    client = genai.Client()
    print("Testing async call...")
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents="You are a dog. Bark and translate.",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BarkOutput,
            ),
        )
        print("Success!")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
