import os
import json
import requests
from datetime import datetime, timedelta
import socket

def generate_ai_summary():
    # ... (Keep your get_recent_logs function exactly as it was) ...
    print(f"[{datetime.now()}] Initializing AI Log Analysis Engine...")
    logs = get_recent_logs()
    
    # ... (Keep your logic for logs and prompts) ...

    # UPDATED REQUEST BLOCK
    api_key = os.getenv("LLM_API_KEY")
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {"max_new_tokens": 150, "temperature": 0.3}
    }

    try:
        # Force the request to use system DNS resolution
        response = requests.post(url, headers=headers, json=payload, timeout=60, verify=True)
        if response.status_code == 200:
            summary = response.json()[0]['generated_text'].strip()
        else:
            summary = f"API Service returned error: {response.status_code}"
    except Exception as e:
        summary = f"Network Error: DNS Resolution failed. Please check network connectivity."

    # ... (Keep your save logic) ...
