import requests
import json

API_KEY = "YOUR_V98_API_KEY_HERE"
BASE_URL = "https://v98store.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def check_models():
    print(f"Checking models at {BASE_URL}/models...")
    try:
        response = requests.get(f"{BASE_URL}/models", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("Models available:")
            model_ids = [m['id'] for m in data.get('data', [])]
            for mid in model_ids:
                print(f" - {mid}")
            return model_ids
        else:
            print(f"Error checking models: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception checking models: {e}")
        return []

def test_chat(model):
    print(f"\nTesting chat completion with model: {model}")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello! What model are you?"}],
        "max_tokens": 100
    }
    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    ids = check_models()
    
    # Check for specific user request "claude 4.6 opus"
    target = None
    for i in ids:
        if "claude" in i.lower() and "opus" in i.lower():
            print(f"Found candidate: {i}")
            if "4.6" in i:
                target = i
                break
    
    if not target and ids:
        print("Explicit 'claude 4.6 opus' not found. Trying first available Claude Opus model if any...")
        for i in ids:
            if "claude" in i.lower() and "opus" in i.lower():
                target = i
                break
    
    if target:
        test_chat(target)
    else:
        print("No Claude Opus model found. Testing 'gpt-3.5-turbo' or first available if present.")
        if "gpt-3.5-turbo" in ids:
            test_chat("gpt-3.5-turbo")
        elif ids:
            test_chat(ids[0])
