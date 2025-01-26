import requests
import json  

url = "https://bf01-34-142-255-125.ngrok-free.app/api/generate" 
data = {
    "model": "llama3.2:1b",
    "prompt": "another one",
    "conversation": [
        {"role": "user", "content": "tell me a joke"},
        {"role": "assistant", "content": "Why scientist dont trust atoms? Because they make up everything"}
    ]
}

try:
    response = requests.post(url, json=data, stream=True)  # Use stream=True for chunked responses
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    full_text = ''
    for chunk in response.iter_lines():
        if chunk:
            data = json.loads(chunk.decode('utf-8'))  # Corrected json usage
            full_text += data.get("response", "")
            if data.get("done"):
                break
    print(full_text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


