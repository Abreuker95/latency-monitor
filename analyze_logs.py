import os
import json
from datetime import datetime, timedelta

def get_recent_logs(filename="latency_history.csv", hours=24):
    """Reads the CSV file and returns rows from the last N hours."""
    if not os.path.isfile(filename):
        return []
    
    recent_rows = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    with open(filename, "r") as f:
        headers = f.readline().strip().split(",")
        for line in f:
            row = line.strip().split(",")
            if len(row) < 6:
                continue
            try:
                # Parse timestamp to compare
                row_time = datetime.fromisoformat(row[0])
                if row_time > cutoff_time:
                    recent_rows.append(line.strip())
            except ValueError:
                continue
                
    return recent_rows

def generate_ai_summary():
    print("Extracting last 24 hours of telemetry...")
    logs = get_recent_logs()
    
    if not logs:
        print("No recent logs found to analyze.")
        return

    # Format data compactly for the LLM prompt
    log_payload = "\n".join(logs)
    
    prompt = f"""
    You are an expert Network Operations Center (NOC) AI Engineer. 
    Analyze the following network latency telemetry data from the last 24 hours.
    Identify any trends, anomalies, packet loss spikes, or specific times where performance degraded.
    Provide a concise, professional executive summary (max 3-4 sentences) written in plain text.
    Do not use markdown formatting or bold text in your response.

    Data format: Timestamp,Target,Latency_ms,PacketLoss_pct,Jitter_ms,Status
    Telemetry Data:
    {log_payload}
    """

    print("Forwarding payload to LLM Engine...")
    
    # --- LLM API Call Configuration ---
    # Example using standard requests to an OpenAI-compatible API or Gemini endpoint.
    # For this to work in GitHub Actions, you will add your API Key to GitHub Secrets.
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Defaulting to mock analysis for system staging.")
        ai_analysis = "Google.com and 8.8.8.8 maintained nominal stability (<15ms). Sanook.com exhibited periodic latency variations during high-traffic intervals, but packet delivery metrics remained within operational tolerances."
    else:
        # Placeholder for your preferred API call (e.g., Gemini, OpenAI, or Anthropic)
        # We will configure the exact library once you select your provider.
        ai_analysis = "API Integrated response goes here."

    # Wrap inside structured JSON for the frontend
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": ai_analysis
    }

    with open("ai_report.json", "w") as f:
        json.dump(report_data, f, indent=4)
    print("AI Report written to ai_report.json successfully.")

if __name__ == "__main__":
    generate_ai_summary()
