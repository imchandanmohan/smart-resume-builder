import os
import requests
from dotenv import load_dotenv

def call_groq_api(messages, temperature=0.7, max_tokens=100):
    """
    Sends a list of messages to the Groq API and returns the JSON response.

    Parameters:
    - messages (list): List of messages in OpenAI format [{'role': 'system'/'user'/'assistant', 'content': '...'}]
    - temperature (float): Controls the randomness of the response.
    - max_tokens (int): Max tokens to generate in the response.

    Returns:
    - dict: The JSON response from the API.
    """
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")

    api_url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Test it
def main():
    messages = [
        {"role": "system", "content": "Act like a friendly customer service agent."},
        {"role": "user", "content": "Say welcome!"}
    ]

    response_data = call_groq_api(messages, temperature=0.5, max_tokens=100)
    
    if response_data:
        assistant_reply = response_data.get("choices", [])[0].get("message", {}).get("content", "")
        print("Assistant's Reply:", assistant_reply)

if __name__ == "__main__":
    main()
