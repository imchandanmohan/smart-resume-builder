# pylint: disable=missing-module-docstring, missing-function-docstring, missing-timeout, inconsistent-return-statements, wrong-import-order

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
TOGETHER_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

def query_together_ai(prompt: str) -> str:
    if not TOGETHER_KEY:
        raise ValueError("TOGETHER_API_KEY not found in .env")

    system_message = (
        "You are an expert at extracting structured information from job descriptions. "
        "Return only the requested info in plain text with no extra commentary."
    )
    full_prompt = f"{system_message}\n\n{prompt}"

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai",
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.7
    }

    retries = 3
    for attempt in range(retries):
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 429:
                time.sleep(60)
                continue
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return "Error processing the request."
