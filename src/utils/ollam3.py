import requests

data = {
    "model": "llama3",
    "prompt": "Explain merge sort algorithm in simple terms",
    "stream": False
}

response = requests.post("http://localhost:11434/api/generate", json=data)
print(response.json()["response"])
