import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def run_face_swap(source_image_url: str, target_image_url: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.deepai.org/api/faceswap",
            headers={"api-key": os.getenv("DEEPAI_API_KEY", "quickstart-QUdJIGlzIGF3ZXNvbWU")},
            data={
                "image": source_image_url,
                "face_image": target_image_url,
            }
        )
        result = response.json()
        return result.get("output_url", "")