import json
import logging
import os
import random
import subprocess  # Import subprocess for using less
from datetime import datetime, timedelta, timezone
from faker import Faker
import ipaddress

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

# Function to select a random IP address from a given CIDR block
def get_random_ip(cidr_block):
    try:
        network = ipaddress.IPv4Network(cidr_block, strict=False)
        # Generate a random IP address within the network
        ip_address = network.network_address + random.randint(0, network.num_addresses - 1)
        return str(ip_address)
    except ipaddress.AddressValueError as e:
        print(f"Error: {cidr_block} is not a valid network: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error generating IP from {cidr_block}: {e}")
        return None
        
# Function to select a random IP and its corresponding country
def get_random_ip_and_country():
    country = random.choice(list(COUNTRY_IP_BLOCKS.keys()))
    cidr_block = random.choice(COUNTRY_IP_BLOCKS[country])
    ip = get_random_ip(cidr_block)
    if ip:
        return ip, country
    else:
        print(f"Failed to generate IP for {country} from {cidr_block}")
        return get_random_ip_and_country()  # Retry until a valid IP is generated

# Load configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Generate Zscaler log with realistic IPs and content
def generate_zscaler_log(config, user, hostname, url, referer, action, reason, url_category="General Browsing"):
    now = datetime.now(timezone.utc)
    server_ip, server_country = get_random_ip_and_country()
    client_ip, client_country = get_random_ip_and_country()

    log_entry = {
        "sourcetype": "zscalernss-web",
        "event": {
            "datetime": (now - timedelta(minutes=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
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
            "useragent": user['user_agent'],  # Use 'user_agent' from config
            "product": "NSS",
            "location": server_country,
            "ClientIP": client_ip,
            "status": random.choice(["200", "404", "500"]),
            "user": user["username"],  # Changed from 'email' to 'username'
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
    return log_entry

# Generate regular log
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
        reason="Normal traffic"
    )
    return log

# Generate suspicious allowed traffic log
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
        url_category=url_category
    )
    return log

# Generate bad traffic log
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
        reason="Unauthorized access attempt"
    )
    return log

# Display sample log and curl command
def display_sample_log_and_curl():
    try:
        config = load_config()
        if not check_required_fields(config):
            return
        
        # Generate one good traffic log and one bad traffic log
        good_log = generate_regular_log(config)
        bad_log = generate_bad_traffic_log(config)

        # Prepare output for less
        output = []

        # Display only one good traffic log
        log_str = json.dumps(good_log, indent=4)
        output.append("\n--- Good Traffic Log ---")
        output.append(log_str)
        api_url = config.get('zscaler_api_url')
        api_key = config.get('zscaler_api_key')
        curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{log_str}'"
        output.append(f"\nCurl command to send the good traffic log to NGSIEM:\n\n{curl_command}\n")

        # Display only one bad traffic log
        log_str = json.dumps(bad_log, indent=4)
        output.append("\n--- Bad Traffic Log ---")
        output.append(log_str)
        curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{log_str}'"
        output.append(f"\nCurl command to send the bad traffic log to NGSIEM:\n\n{curl_command}\n")

        output.append("\nNote: The logs above are samples and have not been sent to NGSIEM. The curl commands provided can be used to send these logs to NGSIEM.\n")
        
        # Use less to display output
        subprocess.run(['less'], input='\n'.join(output).encode('utf-8'))

    except ValueError as e:
        print(f"Error: {e}")


# Check required fields
def check_required_fields(config):
    required_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        print(f"Missing required configuration fields: {', '.join(missing_fields)}")
        return False
    return True

if __name__ == "__main__":
    display_sample_log_and_curl()