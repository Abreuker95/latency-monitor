import os
import json
import requests
from datetime import datetime, timedelta

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
            response = requests.post(url, headers=headers, json=payload, timeout=30)
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
