import os
import json
import requests
from datetime import datetime, timedelta
import socket
from urllib3.util.connection import create_connection

# --- 1. THE DNS BYPASS PATCH ---
# Force the connection to resolve the hostname explicitly to bypass runner restrictions
def patched_create_connection(address, *args, **kwargs):
    host, port = address
    hostname = socket.gethostbyname(host)
    return create_connection((hostname, port), *args, **kwargs)

# Apply the patch to the requests library
requests.packages.urllib3.util.connection.create_connection = patched_create_connection

def get_recent_logs(filename="latency_history.csv", hours=24):
    """Parses the CSV and returns lines from the last 24 hours."""
    if not os.path.isfile(filename):
        return []
    
    recent_rows = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    with open(filename, "r") as f:
        next(f) # Skip header
        for line in f:
            cols = line.strip().split(",")
            if len(cols) < 6: continue
            try:
                if datetime.fromisoformat(cols[0]) > cutoff:
                    recent_rows.append(line.strip())
            except: continue
    return recent_rows

def generate_ai_summary():
    print(f"[{datetime.now()}] Starting AI Analysis...")
    
    # --- 2. NETWORK VISIBILITY CHECK ---
    print("Checking network visibility...")
    try:
        ip = socket.gethostbyname("api-inference.huggingface.co")
        print(f"Successfully resolved HuggingFace IP: {ip}")
    except Exception as e:
        print(f"DNS Resolution FAILED: {e}")

    logs = get_recent_logs()
    
    if not logs:
        summary = "No telemetry data available for the last 24 hours."
    else:
        # Prepare the prompt
        log_payload = "\n".join(logs)
        prompt = f"Analyze this NOC telemetry data: {log_payload}. Provide a professional 3-sentence summary of network health. Do not use markdown."

        # Call HuggingFace
        api_key = os.getenv("LLM_API_KEY")
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": f"<s>[INST] {prompt} [/INST]",
            "parameters": {"max_new_tokens": 150, "temperature": 0.3}
        }

        try:
            # The timeout is set to 60s, and it will now use our patched DNS resolver
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                summary = response.json()[0]['generated_text'].strip()
            else:
                summary = f"API Service reached but returned error: {response.status_code}"
        except Exception as e:
            summary = f"Analysis Engine Connection Error: {str(e)}"

    # Save output
    report = {"generated_at": datetime.now().isoformat(), "summary": summary}
    with open("ai_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("AI report saved.")

if __name__ == "__main__":
    generate_ai_summary()
