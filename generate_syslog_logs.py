import os
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
        'timestamp': 'Jan 01 00:00:00',
        'hostname': 'default-host',
        'drone_id': 'N/A',
        'station_id': 'N/A',
        'battery_level': '100',
        'product_gps_longitude': '0.0',
        'product_gps_latitude': '0.0',
        'flying_state': 'landed',
        'speed_vx': '0',
        'speed_vy': '0',
        'speed_vz': '0',
        'altitude': '0',
        'angle_phi': '0',
        'angle_theta': '0',
        'angle_psi': '0',
        'wifi_signal': 'strong',
        'ip_address': '0.0.0.0',
        'source_ip': '0.0.0.0',
        'destination_ip': '0.0.0.0',
        'source_port': '0',
        'destination_port': '0',
        'username': 'unknown',
        'command': 'none',
        'translated_ip': '0.0.0.0',
        'attack_type': 'none',
        'duration': '0',
        'bytes': '0',
        'port': '0',
        'syslog_ip': '0.0.0.0',
        'rack_id': '1',
        'eventID': '0000'
    }

    # Update log_data with default values where keys are missing
    for key, value in default_values.items():
        log_data.setdefault(key, value)

    return template.format(**log_data)

def generate_random_high_port():
    return random.randint(1024, 65535)

def generate_random_gps_coordinates(region):
    coordinates = {
        "US": {"lat": random.uniform(25.0, 49.0), "long": random.uniform(-125.0, -66.0)},
        "SouthAmerica": {"lat": random.uniform(-55.0, 12.0), "long": random.uniform(-81.0, -34.0)},
        "Australia": {"lat": random.uniform(-44.0, -10.0), "long": random.uniform(113.0, 154.0)},
        "Africa": {"lat": random.uniform(-35.0, 37.0), "long": random.uniform(-17.0, 51.0)},
        "Japan": {"lat": random.uniform(24.0, 46.0), "long": random.uniform(123.0, 146.0)}
    }
    return coordinates[region]

def generate_drones(num_drones):
    drones = []
    regions = ["US", "SouthAmerica", "Australia", "Africa", "Japan"]
    for i in range(num_drones):
        region = random.choice(regions)
        gps = generate_random_gps_coordinates(region)
        drone = {
            "drone_id": f"DRONE_{i+1}",
            "station_id": f"ST_{region}_{i+1}",
            "battery_level": random.randint(20, 100),
            "product_gps_longitude": gps["long"],
            "product_gps_latitude": gps["lat"],
            "flying_state": random.choice(["hovering", "moving", "landing", "idle"]),
            "speed_vx": random.randint(-20, 20),
            "speed_vy": random.randint(-20, 20),
            "speed_vz": random.randint(-10, 10),
            "altitude": random.randint(0, 500),
            "angle_phi": random.uniform(-10.0, 10.0),
            "angle_theta": random.uniform(-10.0, 10.0),
            "angle_psi": random.uniform(-10.0, 10.0),
            "wifi_signal": random.choice(["excellent", "good", "weak", "critical"])
        }
        drones.append(drone)
    return drones

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

        log_data = {
            'pri': pri,
            'timestamp': timestamp,
            'hostname': hostname,
            'app_name': app_name,
            'procid': procid,
            'client_ip': user["client_ip"],
            'source_ip': user["client_ip"],
            'destination_ip': random.choice(config.get('bird_related_ips', ['0.0.0.0'])),
            'source_port': generate_random_high_port(),
            'destination_port': generate_random_high_port(),
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

def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

def send_logs_to_syslog_server(logs, server_ip='127.0.0.1', port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for log_entry in logs:
        sock.sendto(log_entry.encode(), (server_ip, port))
    sock.close()

# Function to generate and send logs to syslog server or file
def generate_and_send_logs():
    try:
        sample_logs = generate_sample_syslogs()
        write_syslog_to_file(sample_logs)
        send_logs_to_syslog_server(sample_logs)
        print(f"Generated {len(sample_logs)} logs, saved to {SYSLOG_FILE}, and sent to syslog server.")
    except Exception as e:
        print(f"Error generating logs: {e}")

if __name__ == "__main__":
    generate_and_send_logs()