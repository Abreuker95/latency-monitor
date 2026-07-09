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
    print(f"[{datetime.now()}] Starting AI Analysis via Google Gemini Engine...")
    logs = get_recent_logs()
    
    if not logs:
        summary = "No telemetry data available for the last 24 hours."
    else:
        log_payload = "\n".join(logs)
        prompt = f"You are a NOC Engineer. Analyze this network telemetry data: {log_payload}. Provide a professional 3-sentence summary of the network's health. Do not use markdown formatting, bolding, or asterisks."

        api_key = os.getenv("LLM_API_KEY")
        
        # --- GEMINI REST API INTEGRATION ---
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, 
                "maxOutputTokens": 150
            }
        }

        try:
            print("Forwarding payload to Google Gemini 2.5 Flash...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                # Parse Gemini's specific JSON structure
                summary = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                summary = f"Gemini API returned error: {response.status_code} - {response.text}"
        except Exception as e:
            summary = f"API Connection Error: {str(e)}"

    # Save output for the dashboard
    report = {"generated_at": datetime.now().isoformat(), "summary": summary}
    with open("ai_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("AI report saved successfully.")

if __name__ == "__main__":
    generate_ai_summary()
