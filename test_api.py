import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key[:25]}...")

url = "https://api.openai.com/v1/embeddings"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "text-embedding-3-small",
    "input": "Hello world"
}

print("\nMaking request to OpenAI API...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Embedding dimensions: {len(result['data'][0]['embedding'])}")
        print("SUCCESS!")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
