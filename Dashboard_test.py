import os
import json
import time
import socket
from datetime import datetime

class NetworkLatencyMonitor:
    def __init__(self, targets, ping_count=5):
        self.targets = targets
        self.ping_count = ping_count
        self.json_output = "latency_data.json"
        self.history_output = "latency_history.csv"

    def tcp_ping(self, target):
        """Pings a target using TCP to bypass cloud ICMP firewalls."""
        latencies = []
        # Target port 53 for DNS (8.8.8.8) and port 443 for standard web hosts
        port = 53 if target == "8.8.8.8" else 443 
        
        for _ in range(self.ping_count):
            try:
                start = time.perf_counter()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2.0)
                    sock.connect((target, port))
                roundtrip = (time.perf_counter() - start) * 1000
                latencies.append(roundtrip)
            except OSError:
                pass
            time.sleep(0.2)
            
        received = len(latencies)
        loss_pct = round(((self.ping_count - received) / self.ping_count) * 100)

        if received == 0:
            return {
                "target": target, 
                "latency_ms": "Timeout", 
                "packet_loss_pct": 100, 
                "jitter_ms": 0, 
                "status": "Offline",
                "timestamp": datetime.now().isoformat()
            }

        avg_latency = round(sum(latencies) / received)
        
        jitter = 0
        if received > 1:
            diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
            jitter = round(sum(diffs) / len(diffs), 1)

        status = "Online" if loss_pct < 50 else "Degraded"

        return {
            "target": target,
            "latency_ms": avg_latency,
            "packet_loss_pct": loss_pct,
            "jitter_ms": jitter,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

    def log_to_history(self, results):
        """Appends telemetry to a continuous CSV file for long-term trend mapping."""
        file_exists = os.path.isfile(self.history_output)
        with open(self.history_output, "a") as f:
            if not file_exists:
                f.write("Timestamp,Target,Latency_ms,PacketLoss_pct,Jitter_ms,Status\n")
            for r in results:
                f.write(f"{r['timestamp']},{r['target']},{r['latency_ms']},{r['packet_loss_pct']},{r['jitter_ms']},{r['status']}\n")

    def save_live_dashboard_data(self, results):
        """Updates the primary JSON payload fetched by the frontend dashboard."""
        with open(self.json_output, "w") as f:
            json.dump(results, f, indent=4)

    def execute(self):
        print(f"[{datetime.now()}] Initializing NLM Observability Suite...")
        results = []
        for target in self.targets:
            print(f"Polling {target} via TCP...")
            results.append(self.tcp_ping(target))
        
        self.save_live_dashboard_data(results)
        self.log_to_history(results)
        print("Telemetry updated successfully.")

if __name__ == "__main__":
    monitored_hosts = ["google.com", "8.8.8.8", "sanook.com"]
    monitor = NetworkLatencyMonitor(targets=monitored_hosts)
    monitor.execute()
