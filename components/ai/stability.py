import os
import base64
import requests
from dotenv import load_dotenv, find_dotenv

def generate_text_to_image():
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    url = f"{api_host}/v1/user/balance"

    _ = load_dotenv(find_dotenv())  # read local .env file
    api_key = os.getenv("STABILITY_API_KEY")
    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": "An image of an anime character, or an anime scenery with anime characters"
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
            "style_preset":"anime",
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    for i, image in enumerate(data["artifacts"]):
        with open(f"v1_txt2img_{i}.png", "wb") as f:
            f.write(base64.b64decode(image["base64"]))