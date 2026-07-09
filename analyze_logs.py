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
    print(f"[{datetime.now()}] Starting AI Analysis via API Gateway...")
    logs = get_recent_logs()
    
    if not logs:
        summary = "No telemetry data available for the last 24 hours."
    else:
        log_payload = "\n".join(logs)
        raw_prompt = f"Analyze this NOC telemetry data: {log_payload}. Provide a professional 3-sentence summary of network health. Do not use markdown."
        formatted_prompt = f"<s>[INST] {raw_prompt} [/INST]"

        api_key = os.getenv("LLM_API_KEY")
        
        # --- THE PROXY BYPASS ---
        # Routing through your newly deployed Google Apps Script Gateway
        PROXY_URL = "https://script.google.com/macros/s/AKfycbw3aE34SJ1q0LhbNcJodFYBP2h_EQS6okV2nOooyli8AWT-OIzebvgtz5ByQnBCKYwp/exec"
        
        payload = {
            "prompt": formatted_prompt,
            "apiKey": api_key
        }

        try:
            print("Routing request through Google Apps Script Gateway...")
            response = requests.post(PROXY_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                # Parse the array returned by HuggingFace via the proxy
                summary = response.json()[0]['generated_text'].strip()
            else:
                summary = f"Proxy reached but returned error: {response.status_code}"
        except Exception as e:
            summary = f"Gateway Connection Error: {str(e)}"

    report = {"generated_at": datetime.now().isoformat(), "summary": summary}
    with open("ai_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("AI report saved.")

if __name__ == "__main__":
    generate_ai_summary()
