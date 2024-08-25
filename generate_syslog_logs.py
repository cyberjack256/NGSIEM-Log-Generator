import socket
import json
import logging
import os
import random
import time
import threading
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths to config files
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
MESSAGE_CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/message.config')
SYSLOG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/syslog.log')
EXECUTION_LOG = os.path.expanduser('~/NGSIEM-Log-Generator/generate_syslog_logs_execution.log')

# Syslog server details
SYSLOG_SERVER_IP = '127.0.0.1'  # Change to your aggregator IP if needed
SYSLOG_SERVER_PORT = 514

# Load configuration
def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Generate the PRI value based on RFC 5424
def calculate_pri(facility, severity):
    return (facility * 8) + severity

# Generate realistic sample syslogs following RFC 5424
def generate_syslog_message(template, pri, timestamp, hostname, app_name, procid, **kwargs):
    return template.format(
        pri=pri,
        timestamp=timestamp,
        hostname=hostname,
        app_name=app_name,
        procid=procid,
        **kwargs
    )

# Generate a single syslog log
def generate_single_syslog():
    config = load_config(MESSAGE_CONFIG_FILE)
    now = datetime.now(timezone.utc)
    
    hostnames = [
        "dronebase.local",
        "firewallcontrol.local",
        "analyticsengine.local",
        "securitygateway.local",
        "datacenter.local"
    ]
    
    hostname = random.choice(hostnames)
    app_name = "DroneController"
    procid = str(random.randint(1000, 9999))
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    message_template = random.choice(config['info'])  # Change 'info' to any other log type as needed
    kwargs = {
        "drone_id": f"DR{random.randint(100, 999)}",
        "station_id": f"ST{random.randint(1, 10)}",
        "battery_level": random.randint(0, 100),
        "product_gps_longitude": round(random.uniform(-180, 180), 6),
        "product_gps_latitude": round(random.uniform(-90, 90), 6),
        "flying_state": random.choice(["hovering", "flying", "landed"]),
        "speed_vx": random.randint(-50, 50),
        "speed_vy": random.randint(-50, 50),
        "speed_vz": random.randint(-50, 50),
        "altitude": round(random.uniform(0, 500), 2),
        "angle_phi": round(random.uniform(-180, 180), 2),
        "angle_theta": round(random.uniform(-90, 90), 2),
        "angle_psi": round(random.uniform(0, 360), 2),
        "wifi_signal": random.randint(0, 100),
        "source_ip": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "destination_ip": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "username": random.choice(["admin", "guest", "operator"]),
        "command": random.choice(["reboot", "shutdown", "status check"]),
        "attack_type": random.choice(["SQL Injection", "DDoS", "Phishing"]),
    }

    pri = calculate_pri(1, 6)  # Example PRI calculation
    return generate_syslog_message(
        template=message_template,
        pri=pri,
        timestamp=timestamp,
        hostname=hostname,
        app_name=app_name,
        procid=procid,
        **kwargs
    )

# Generate and send a batch of syslog logs
def generate_batch_syslogs(num_logs=100):
    config = load_config(MESSAGE_CONFIG_FILE)
    logs = []

    for _ in range(num_logs):
        log = generate_single_syslog()
        logs.append(log)

    # Write logs to file
    write_syslog_to_file(logs)
    
    # Send logs via UDP to the syslog server
    send_logs_via_udp(logs)

# Write syslog to file
def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

# Send syslog logs via UDP to a syslog server
def send_logs_via_udp(logs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for log in logs:
        sock.sendto(log.encode('utf-8'), (SYSLOG_SERVER_IP, SYSLOG_SERVER_PORT))
    sock.close()

# Background service to generate and send logs continuously
def background_log_service():
    while True:
        generate_batch_syslogs(num_logs=random.randint(80, 120))  # Generates between 80 to 120 logs per batch
        time.sleep(random.uniform(0.5, 1.5))  # Sleep for a random time between 0.5 to 1.5 seconds

# Start background service
def start_background_service():
    thread = threading.Thread(target=background_log_service)
    thread.daemon = True  # Run in background
    thread.start()
    print("Background log generation service started.")

# Main function to generate logs
if __name__ == "__main__":
    start_background_service()
    input("Press Enter to stop the service...\n")