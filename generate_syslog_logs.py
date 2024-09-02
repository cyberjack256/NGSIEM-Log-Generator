import os
import time
import json
from datetime import datetime, timedelta, timezone
import random
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths to config files
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
MESSAGE_CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/message.config')
SYSLOG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/syslog.log')

def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def generate_syslog_message(template, **log_data):
    # Default values for missing keys
    default_values = {
        'timestamp': datetime.now().strftime('%b %d %H:%M:%S'),
        'hostname': 'default-host',
        'drone_id': 'DRONE-' + str(random.randint(1000, 9999)),
        'station_id': 'STATION-' + str(random.randint(1, 10)),
        'battery_level': random.randint(20, 100),  # Simulate a range for battery level
        'product_gps_longitude': round(random.uniform(-180, 180), 6),  # Longitude range
        'product_gps_latitude': round(random.uniform(-90, 90), 6),  # Latitude range
        'flying_state': random.choice(['landed', 'flying', 'hovering', 'landing']),
        'speed_vx': random.randint(0, 50),
        'speed_vy': random.randint(0, 50),
        'speed_vz': random.randint(0, 50),
        'altitude': random.randint(0, 500),  # Simulate realistic altitude
        'angle_phi': random.randint(0, 360),
        'angle_theta': random.randint(0, 360),
        'angle_psi': random.randint(0, 360),
        'wifi_signal': random.choice(['weak', 'medium', 'strong']),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'source_ip': '192.168.' + str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)),
        'destination_ip': '192.168.' + str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)),
        'source_port': str(random.randint(1024, 65535)),
        'destination_port': str(random.choice([80, 443, 22, 8080, 53])),
        'username': random.choice(['sparrow', 'eagle', 'owl']),
        'command': random.choice(['ls -la', 'netstat -an', 'ps aux']),
        'translated_ip': '192.168.' + str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)),
        'attack_type': random.choice(['brute-force', 'DDoS', 'port-scan']),
        'duration': random.randint(1, 60),  # Duration in minutes
        'bytes': random.randint(100, 10000),  # Data transferred
        'port': str(random.choice([80, 443, 22, 8080, 53])),
        'syslog_ip': '192.168.' + str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)),
        'rack_id': str(random.randint(1, 10)),
        'eventID': 'EVT-' + str(random.randint(1000, 9999))
    }

    # Update log_data with default values where keys are missing
    for key, value in default_values.items():
        log_data.setdefault(key, value)

    return template.format(**log_data)

def generate_sample_syslogs():
    config = load_config(CONFIG_FILE)
    message_config = load_config(MESSAGE_CONFIG_FILE)
    now = datetime.now(timezone.utc)

    hostnames = [
        "birdcentral.nest.local",
        "nestaccess.adminbird.net",
        "birdwatch.cams.net",
        "birdnet.secure.local",
        "nestwall.firewall.local"
    ]
    users = config.get('users', [])
    log_facility = 1  # User-level messages (typically facility 1)
    severity = 6  # Informational
    pri = (log_facility * 8) + severity

    if not users:
        raise ValueError("No users found in the configuration.")

    messages = message_config.get('info', [])

    sample_logs = []
    for _ in range(80):  # Generate 80 logs
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = random.choice([
            "NestAccess",
            "BirdNet",
            "BirdWatch",
            "NestWall",
            "BirdCentral"
        ])
        procid = str(random.randint(1000, 9999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%b %d %H:%M:%S')
        message_template = random.choice(messages)
        srcPort = str(random.randint(1024, 65535))

        log_data = {
            'pri': pri,
            'timestamp': timestamp,
            'hostname': hostname,
            'app_name': app_name,
            'procid': procid,
            'client_ip': user["client_ip"],
            'public_ip': random.choice(config.get('bird_related_ips', ['0.0.0.0'])),  # Use bird-related IP
            'srcPort': srcPort,
            'username': user["username"],
            'mac_address': user["mac_address"],
            'user_agent': user["user_agent"]
        }

        message = generate_syslog_message(
            template=message_template,
            **log_data
        )

        sample_logs.append(message)
    
    return sample_logs

def check_send_to_syslog_service_status():
    """
    Check if the syslog sending service is running.
    """
    try:
        result = subprocess.run(['pgrep', '-fl', 'send_syslog.py'], capture_output=True, text=True)
        if result.stdout:
            print("Syslog sending service is running.")
        else:
            print("Syslog sending service is not running.")
    except Exception as e:
        print(f"Failed to check syslog sending service status: {e}")

def stop_send_to_syslog_service():
    """
    Stop the syslog sending service.
    """
    try:
        print("Stopping the syslog sending service...")
        result = subprocess.run(['pkill', '-f', 'send_syslog.py'])
        if result.returncode == 0:
            print("Syslog sending service stopped successfully.")
        else:
            print("Syslog sending service was not running or failed to stop.")
    except Exception as e:
        print(f"Failed to stop syslog sending service: {e}")

def send_to_syslog_service():
    """
    Continuously send logs to the syslog service at a rate of 200 logs per second.
    """
    config = load_config(CONFIG_FILE)
    syslog_server = config.get('syslog_server', 'localhost')
    syslog_port = config.get('syslog_port', 514)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            sample_logs = generate_sample_syslogs()
            for log in sample_logs:
                sock.sendto(log.encode('utf-8'), (syslog_server, syslog_port))
            
            # To maintain a rate of 200 logs per second
            time.sleep(1 / 200.0)  # 200 logs per second
    except KeyboardInterrupt:
        print("\nStopping syslog sending service.")
    finally:
        sock.close()

def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

# Add code to generate and save logs to a file
def generate_and_save_logs():
    try:
        sample_logs = generate_sample_syslogs()
        write_syslog_to_file(sample_logs)
        print(f"Generated {len(sample_logs)} logs and saved to {SYSLOG_FILE}.")
    except Exception as e:
        print(f"Error generating logs: {e}")

if __name__ == "__main__":
    generate_and_save_logs()
