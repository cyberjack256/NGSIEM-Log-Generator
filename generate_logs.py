import json
import logging
import os
import random
import requests
import time
from datetime import datetime, timedelta, timezone
from faker import Faker
import ipaddress
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
fake = Faker()

# Real public IP ranges from 15 US-friendly countries
COUNTRY_IP_BLOCKS = {
    "United States": ["3.0.0.0/8", "8.8.8.0/24", "13.52.0.0/14", "34.192.0.0/12"],
    "Canada": ["24.48.0.0/12", "47.96.0.0/11", "104.128.0.0/11", "205.251.192.0/19"],
    "United Kingdom": ["51.140.0.0/12", "88.0.0.0/11", "91.128.0.0/11", "185.0.0.0/8"],
    "Australia": ["13.54.0.0/15", "101.0.0.0/22", "203.0.0.0/24", "203.2.0.0/16"],
    "Germany": ["5.8.8.0/21", "31.172.0.0/14", "46.16.0.0/12", "195.20.0.0/15"],
    "France": ["5.39.0.0/16", "37.0.0.0/13", "62.160.0.0/11", "212.198.0.0/16"],
    "Japan": ["27.0.0.0/8", "43.240.0.0/12", "150.95.0.0/16", "203.112.0.0/14"],
    "South Korea": ["1.200.0.0/13", "58.120.0.0/13", "119.192.0.0/13", "175.192.0.0/12"],
    "Italy": ["5.88.0.0/13", "37.160.0.0/13", "151.0.0.0/13", "185.48.0.0/12"],
    "Netherlands": ["37.128.0.0/11", "77.160.0.0/12", "145.128.0.0/9", "195.64.0.0/13"],
    "Sweden": ["31.208.0.0/12", "83.0.0.0/11", "185.0.0.0/10", "193.10.0.0/16"],
    "Switzerland": ["5.144.0.0/13", "31.128.0.0/11", "185.24.0.0/12", "213.3.0.0/16"],
    "Norway": ["37.0.0.0/12", "77.16.0.0/12", "84.0.0.0/13", "185.0.0.0/11"],
    "Denmark": ["31.3.0.0/18", "80.160.0.0/11", "185.15.0.0/12", "188.128.0.0/12"],
    "Belgium": ["5.128.0.0/13", "37.72.0.0/14", "185.48.0.0/11", "194.0.0.0/11"],
}

def get_random_ip(cidr_block):
    network = ipaddress.IPv4Network(cidr_block)
    return str(ipaddress.IPv4Address(network.network_address + random.randint(0, network.num_addresses - 1)))

def get_random_ip_and_country():
    country = random.choice(list(COUNTRY_IP_BLOCKS.keys()))
    ip = get_random_ip(random.choice(COUNTRY_IP_BLOCKS[country]))
    return ip, country

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def generate_zscaler_log(config, user, hostname, url, referer, action, reason, url_category="General Browsing", event_kind="event", tactic=None, technique=None):
    now = datetime.now(timezone.utc)
    server_ip, server_country = get_random_ip_and_country()
    client_ip, client_country = get_random_ip_and_country()

    log_entry = {
        "sourcetype": "zscalernss-web",
        "event": {
            "datetime": (now - timedelta(minutes=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
            "kind": event_kind,
            "reason": reason,
            "event_id": random.randint(100000, 999999),
            "protocol": "HTTPS",
            "action": action,
            "transactionsize": random.randint(1000, 2000),
            "responsesize": random.randint(500, 1000),
            "requestsize": random.randint(100, 500),
            "urlcategory": url_category,
            "serverip": server_ip,
            "clienttranstime": random.randint(200, 500),
            "requestmethod": random.choice(["GET", "POST"]),
            "refererURL": referer,
            "useragent": random.choice(config.get('user_agents', ['Mozilla/5.0'])),
            "product": "NSS",
            "location": server_country,
            "ClientIP": client_ip,
            "status": random.choice(["200", "404", "500"]),
            "user": user["username"],  # Corrected field from 'email' to 'username'
            "url": url,
            "vendor": "Zscaler",
            "hostname": hostname,
            "clientpublicIP": client_ip,
            "threatcategory": random.choice(["none", "Malware", "Phishing"]),
            "threatname": random.choice(["none", "Trojan", "Adware"]),
            "filetype": random.choice(["application/json", "text/html", "application/octet-stream"]),
            "appname": "browser",
            "pagerisk": random.randint(1, 100),
            "department": random.choice(["IT", "SOC", "Help-Desk"]),
            "urlsupercategory": "information",
            "appclass": random.choice(["Business", "Consumer Apps", "Enterprise", "General Browsing"]),
            "dlpengine": "none",
            "urlclass": random.choice(["Business Use", "Bandwidth Loss", "General Surfing"]),
            "threatclass": "none",
            "dlpdictionaries": "none",
            "fileclass": random.choice(["Images", "Executables Files", "Archive Files"]),
            "bwthrottle": "none",
            "servertranstime": random.randint(100, 300),
            "contenttype": random.choice(["application/octet-stream", "text/plain"]),
            "unscannabletype": "none",
            "deviceowner": "Admin",
            "devicehostname": hostname,
            "decrypted": random.choice(["yes", "no"]),
            "resource_accessed": url if "sensitive-data" in url else "N/A"
        }
    }

    # Include tactic and technique only for alerts
    if event_kind == "alert":
        log_entry["event"]["tactic"] = tactic
        log_entry["event"]["technique"] = technique

    return log_entry

# Generate regular log (normal traffic)
def generate_regular_log(config):
    users = config.get("users", [])
    if not users:
        raise ValueError("No users found in the configuration.")
    user_info = random.choice(users)
    url = f"https://{random.choice(['birdsite.com', 'adminbird.com', 'birdnet.org'])}/{random.choice(['home', 'photos', 'posts', 'videos', 'articles'])}"
    log = generate_zscaler_log(
        config=config,
        user=user_info,
        hostname=user_info['hostname'],
        url=url,
        referer="https://birdsite.com",
        action="allowed",
        reason="Normal traffic",
        event_kind="event"  # Normal traffic is an "event"
    )
    return log

# Generate bad traffic log (alerts)
def generate_bad_traffic_log(config):
    user_info = next((u for u in config.get("users", []) if u['username'] == "eagle"), None)
    if not user_info:
        raise ValueError("User 'eagle' not found in the configuration.")
    log = generate_zscaler_log(
        config=config,
        user=user_info,
        hostname=user_info['hostname'],
        url="https://adminbird.com/login",
        referer="https://birdsite.com/home",
        action="blocked",
        reason="Unauthorized access attempt",
        event_kind="alert",  # Bad traffic triggers an "alert"
        tactic="Credential Access",  # Example tactic
        technique="Brute Force"  # Example technique
    )
    return log

# Generate suspicious allowed traffic log (alerts)
def generate_suspicious_allowed_log(config):
    users = config.get("users", [])
    if not users:
        raise ValueError("No users found in the configuration.")
    user_info = random.choice(users)
    url = f"https://{random.choice(['badsite.com', 'malicioussite.net', 'phishingsite.org'])}"
    url_category = random.choice([
        "Other Advanced Security", "Phishing", "Botnet Protection", "Malicious Content",
        "Peer To Peer (P2P)", "Unauthorized Communication Protection", "Cross-site Scripting (XSS)",
        "Browser Exploit", "Suspicious Destinations Protection", "Spyware Callback", "Web Spam",
        "Suspicious Content", "Cryptomining and Blockchain", "Adware/Spyware Sites", "Custom Encrypted Content",
        "Dynamic DNS Host", "Newly Revived Domains", "Other Security", "Spyware/Adware"
    ])
    log = generate_zscaler_log(
        config=config,
        user=user_info,
        hostname=user_info['hostname'],
        url=url,
        referer="https://birdsite.com",
        action="allowed",
        reason="Suspicious but allowed traffic",
        url_category=url_category,
        event_kind="alert",  # Suspicious traffic also triggers an "alert"
        tactic="Defense Evasion",  # Example tactic
        technique="Obfuscated Files or Information"  # Example technique
    )
    return log

# Display sample log and curl command
def display_sample_log_and_curl():
    try:
        config = load_config()
        if not check_required_fields(config):
            return
        
        good_log = generate_regular_log(config)
        bad_log = generate_bad_traffic_log(config)

        sample_logs = {
            "Good Traffic Log": good_log,
            "Bad Traffic Log": bad_log,
        }

        for log_type, log in sample_logs.items():
            log_str = json.dumps(log, indent=4)
            print(f"\n--- {log_type} ---")
            print(log_str)
            api_url = config.get('zscaler_api_url')
            api_key = config.get('zscaler_api_key')
            curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{log_str}'"
            print(f"\nCurl command to send the {log_type.lower()} to NGSIEM:\n\n{curl_command}\n")

        print("\nNote: The logs above are samples and have not been sent to NGSIEM. The curl commands provided can be used to send these logs to NGSIEM.\n")
    except ValueError as e:
        print(f"Error: {e}")

# Function to run the log generator as a service
def run_as_service(config):
    print("Starting log generation service...")
    try:
        while True:
            num_logs = random.randint(1, 20)  # Generate between 1 and 20 logs per second
            for _ in range(num_logs):
                log_type = random.choices(
                    ["good", "bad"],
                    weights=[0.83, 0.17],  # 83% good traffic, 17% bad/suspicious traffic
                    k=1
                )[0]

                if log_type == "good":
                    log = generate_regular_log(config)
                else:
                    log = generate_bad_traffic_log(config)

                log_str = json.dumps(log)
                api_url = config.get('zscaler_api_url')
                api_key = config.get('zscaler_api_key')
                requests.post(api_url, headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }, data=log_str)
                print(f"Log sent: {log_str}")

            time.sleep(1)  # Pause for a second

    except KeyboardInterrupt:
        print("Service stopped by user.")

# Start logging service
def start_logging_service():
    subprocess.Popen(["python3", os.path.abspath(__file__), "--service"])
    print("Logging service started.")

# Stop logging service
def stop_logging_service():
    subprocess.run(["pkill", "-f", os.path.abspath(__file__)])
    print("Logging service stopped.")

# Check logging service status
def check_logging_service_status():
    result = subprocess.run(["pgrep", "-fl", os.path.abspath(__file__)], capture_output=True, text=True)
    if result.stdout:
        print("Logging service is running.")
    else:
        print("Logging service is not running.")

# Function to check required fields
def check_required_fields(config):
    required_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        print(f"Missing required configuration fields: {', '.join(missing_fields)}")
        return False
    return True

if __name__ == "__main__":
    import sys

    if "--service" in sys.argv:
        config = load_config()
        run_as_service(config)
    else:
        display_sample_log_and_curl()
