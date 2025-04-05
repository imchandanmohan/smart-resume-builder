import requests

def call_grok_api(prompt, input_text, api_key=None):
    endpoint = "https://api.grok.example.com/generate"  # replace with actual
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "input": input_text
    }

    response = requests.post(endpoint, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
