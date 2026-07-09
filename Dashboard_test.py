import subprocess
import platform
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latency(host):
    """
    Pings a host and returns the average latency in milliseconds.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        if 'time=' in output:
            latency = output.split('time=')[1].split(' ')[0].replace('ms', '')
            return float(latency)
        return None
    except subprocess.CalledProcessError:
        return None

def monitor_targets(hosts):
    logging.info("Starting latency monitoring...")
    results = []
    
    for host in hosts:
        latency = get_latency(host)
        status = "Online" if latency else "Offline"
        
        # Structure the data into a dictionary
        results.append({
            "target": host,
            "latency_ms": latency,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        if latency:
            logging.info(f"Target: {host} | Latency: {latency}ms")
        else:
            logging.warning(f"Target: {host} | Status: Unreachable")
            
    return results

def save_to_json(data, filename="latency_data.json"):
    """
    Writes the structured network data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info(f"Data successfully written to {filename}")

if __name__ == "__main__":
    targets = ["google.com", "8.8.8.8", "sanook.com"]
    
    # Run monitor and collect data
    network_data = monitor_targets(targets)
    
    # Save the data to our JSON bridge
    save_to_json(network_data)