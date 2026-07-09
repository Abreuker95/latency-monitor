import os
import json
import requests
from datetime import datetime, timedelta

def get_recent_logs(filename="latency_history.csv", hours=24):
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

def process_system_alerts(logs):
    """Analyzes the most recent logs to trigger ChatOps and Dashboard alerts."""
    print("Evaluating telemetry for active incidents...")
    
    # Grab the last 3 entries (the most recent run for all 3 targets)
    recent_run = logs[-3:] if len(logs) >= 3 else logs
    incidents = []

    for line in recent_run:
        cols = line.strip().split(",")
        target = cols[1]
        status = cols[5]
        try:
            loss = float(cols[3])
        except ValueError:
            continue

        # Trigger logic: If a target drops packets or goes offline
        if status != "Online" or loss > 0:
            incidents.append(f"{target} reporting {loss}% packet loss. Status: {status}")

    if incidents:
        alert_state = "ALERT"
        alert_msg = " | ".join(incidents)
        print(f"[ALERT DETECTED] {alert_msg}")
        
        # Fire Discord Webhook
        discord_url = os.getenv("DISCORD_WEBHOOK")
        if discord_url:
            print("Firing ChatOps Webhook to Discord...")
            payload = {
                "content": "🚨 **AUTOMATED NOC ALERT** 🚨",
                "embeds": [{
                    "title": "Network Degradation Detected",
                    "description": alert_msg,
                    "color": 16711680 # Hex for Red
                }]
            }
            try:
                requests.post(discord_url, json=payload, timeout=10)
            except Exception as e:
                print(f"Discord Webhook Failed: {e}")
    else:
        alert_state = "NORMAL"
        alert_msg = "No recent incidents detected. Infrastructure is stable."
        print("[SYSTEM NORMAL]")

    # Save state for the Frontend Dashboard
    alert_data = {
        "status": alert_state, 
        "message": alert_msg, 
        "timestamp": datetime.now().isoformat()
    }
    with open("alerts.json", "w") as f:
        json.dump(alert_data, f, indent=4)

def generate_ai_summary():
    print(f"[{datetime.now()}] Starting AI Analysis via Google Gemini Engine...")
    logs = get_recent_logs()
    
    # Process alerts before doing the AI summary
    if logs:
        process_system_alerts(logs)
    
    if not logs:
        summary = "No telemetry data available for the last 24 hours."
    else:
        log_payload = "\n".join(logs)
        prompt = f"You are a NOC Engineer. Analyze this network telemetry data: {log_payload}. Provide a professional 3-sentence summary of the network's health. Do not use markdown formatting, bolding, or asterisks."

        api_key = os.getenv("LLM_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, 
                "maxOutputTokens": 500  # <--- BUMPED FROM 150 to 500
            }
        }

        try:
            print("Forwarding payload to Google Gemini...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                summary = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                summary = f"Gemini API returned error: {response.status_code}"
        except Exception as e:
            summary = f"API Connection Error: {str(e)}"

    # --- LOG ROTATION & ARCHIVAL SYSTEM ---
    report_file = "ai_report.json"
    new_entry = {"generated_at": datetime.now().isoformat(), "summary": summary}
    
    if os.path.exists(report_file):
        with open(report_file, "r") as f:
            try:
                history = json.load(f)
                if isinstance(history, dict): history = [history]
            except: history = []
    else: history = []

    history.insert(0, new_entry)
    history = history[:15]

    with open(report_file, "w") as f:
        json.dump(history, f, indent=4)
    print("AI report saved and archive rotated successfully.")

if __name__ == "__main__":
    generate_ai_summary()
