import os
import time
import multiprocessing
from multiprocessing import Value
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

# Global variable to hold the process
send_logs_process = None
# Global shared variable for log count
logs_sent_count = Value('i', 0)  # 'i' is for integer
# Global variables to track log start time and debug logs
log_start_time = None
debug_logs_enabled = True  # Enable debug logs by default after 15 minutes


# Load configuration from a given file path
def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Generate syslog message, including observer_id and ensuring UTC timestamp
def generate_syslog_message(template, **log_data):
    config = load_config(CONFIG_FILE)  # Load the main config
    observer_id = config.get('observer', {}).get('id', 'unknown')
    log_data['observer_id'] = observer_id

    print(f"Observer ID: {observer_id}")  # Debugging output to verify observer.id is loaded

    # Default values for missing keys
    default_values = {
        'timestamp': datetime.now(timezone.utc).strftime('%b %d %H:%M:%S'),  # Use UTC timestamp
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

# Generate sample syslog messages
def generate_sample_syslogs():
    config = load_config(CONFIG_FILE)  # Load the main config
    message_config = load_config(MESSAGE_CONFIG_FILE)  # Load the message config
    now = datetime.now(timezone.utc)  # Current UTC time

    # Fetch observer.id from config
    observer_id = config.get('observer', {}).get('id', 'unknown-observer')

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
        # Ensure that the log's timestamp is always before the current UTC time
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
            'user_agent': user["user_agent"],
            'observer_id': observer_id  # Add observer.id here
        }

        message = generate_syslog_message(
            template=message_template,
            **log_data
        )

        sample_logs.append(message)
    
    return sample_logs

# Check if the syslog sending service is running
def check_send_to_syslog_service_status():
    global send_logs_process, logs_sent_count
    if send_logs_process is not None and send_logs_process.is_alive():
        print(f"Syslog sending service is running. Logs sent: {logs_sent_count.value}")
    else:
        print("Syslog sending service is not running.")

# Stop the syslog sending service
def stop_send_to_syslog_service():
    global send_logs_process
    if send_logs_process is not None and send_logs_process.is_alive():
        send_logs_process.terminate()
        send_logs_process.join()  # Ensure the process has completely stopped
        send_logs_process = None
        print("Syslog sending service stopped successfully.")
    else:
        print("Syslog sending service is not running.")

# Start the syslog sending service
def start_send_to_syslog_service():
    global send_logs_process
    if send_logs_process is None or not send_logs_process.is_alive():
        send_logs_process = multiprocessing.Process(target=send_to_syslog_service)
        send_logs_process.start()
        print("Syslog sending service started.")
    else:
        print("Syslog sending service is already running.")

# Continuously send logs to the syslog service at a rate of 200 logs per second
def send_to_syslog_service():
    global logs_sent_count
    global log_start_time
    global debug_logs_enabled

    config = load_config(CONFIG_FILE)
    syslog_server = config.get('syslog_server', 'localhost')
    syslog_port = config.get('syslog_port', 514)
    
    # Record the time when log sending starts
    log_start_time = datetime.now(timezone.utc)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            sample_logs = generate_sample_syslogs()
            
            # After 15 minutes, enable debug logs if they are still enabled
            time_since_start = datetime.now(timezone.utc) - log_start_time
            if time_since_start >= timedelta(minutes=15) and debug_logs_enabled:
                # Add debug logs to the mix, increasing log volume by 30%
                debug_logs = generate_sample_debug_logs()
                sample_logs.extend(debug_logs)  # Add debug logs on top of existing logs

            for log in sample_logs:
                sock.sendto(log.encode('utf-8'), (syslog_server, syslog_port))
                
                # Update the shared counter
                with logs_sent_count.get_lock():
                    logs_sent_count.value += 1
            
            # To maintain a rate of 200 logs per second
            time.sleep(1 / 200.0)
    except KeyboardInterrupt:
        print("\nStopping syslog sending service.")
    finally:
        sock.close()

# Generate sample debug logs (only if debug_logs_enabled is True)
def generate_sample_debug_logs():
    if not debug_logs_enabled:
        return []  # Return an empty list if debug logs are disabled
    
    message_config = load_config(MESSAGE_CONFIG_FILE)
    
    # Use the debug log template from the config
    debug_logs = []
    for _ in range(24):  # Generate 24 debug logs (30% of the usual 80 logs)
        log_data = {
            'timestamp': datetime.now(timezone.utc).strftime('%b %d %H:%M:%S'),  # Ensure UTC timestamp
            'hostname': 'debug-host',
            'level': 'debug',
            'message': 'This is a simulated debug log message.'
        }
        debug_logs.append(json.dumps(log_data))
    
    return debug_logs

# Write syslog logs to a file
def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

# Generate and save logs to a file
def generate_and_save_logs():
    try:
        sample_logs = generate_sample_syslogs()
        write_syslog_to_file(sample_logs)
        print(f"Generated {len(sample_logs)} logs and saved to {SYSLOG_FILE}.")
    except Exception as e:
        print(f"Error generating logs: {e}")

if __name__ == "__main__":
    generate_and_save_logs()