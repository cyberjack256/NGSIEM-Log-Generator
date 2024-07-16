from datetime import datetime, timedelta
import random

# Generate sample logs
def generate_sample_logs():
    if not validate_config():
        print("\nPlease set the missing configuration fields using option 2.")
        return

    # Generate logs based on the config
    config = load_config()
    current_time = datetime.utcnow()
    time_range = [current_time - timedelta(minutes=5), current_time + timedelta(minutes=5)]
    
    logs = []
    for i in range(5):  # Generate 5 sample logs
        log_time = time_range[0] + (time_range[1] - time_range[0]) * random.random()
        log = {
            "sourcetype": "zscalernss-web",
            "event": {
                "datetime": log_time.strftime("%Y-%m-%d %H:%M:%S"),
                "reason": "allowed",
                "event_id": random.randint(100000, 999999),
                "protocol": "HTTPS",
                "action": "allowed",
                "transactionsize": random.randint(500, 1500),
                "responsesize": random.randint(250, 750),
                "requestsize": random.randint(100, 300),
                "urlcategory": "business",
                "serverip": "192.168.1.100",
                "clienttranstime": random.randint(100, 500),
                "requestmethod": "GET",
                "refererURL": "https://example.com",
                "useragent": random.choice(config['user_agents']),
                "product": "NSS",
                "location": "Office",
                "ClientIP": random.choice(config['ip_addresses']),
                "status": "200",
                "user": random.choice(config['usernames']),
                "url": "https://malicious-site.com",
                "vendor": "Zscaler",
                "hostname": "malicious-site.com",
                "clientpublicIP": random.choice(config['ip_addresses']),
                "threatcategory": "malware",
                "threatname": "MaliciousFile.exe",
                "filetype": "exe",
                "appname": "MalwareApp",
                "pagerisk": random.randint(1, 100),
                "department": "IT",
                "urlsupercategory": "malicious",
                "appclass": "unknown",
                "dlpengine": "engine1",
                "urlclass": "malicious",
                "threatclass": "malware",
                "dlpdictionaries": "dict1",
                "fileclass": "malware",
                "bwthrottle": "none",
                "servertranstime": random.randint(100, 300),
                "contenttype": "application/octet-stream",
                "unscannabletype": "none",
                "deviceowner": "admin",
                "devicehostname": "host1",
                "decrypted": "no"
            }
        }
        logs.append(log)

    print("\nGenerated logs:")
    for log in logs:
        print(json.dumps(log, indent=4))

    # Example command to send logs to NGSIEM
    api_url = config['api_url']
    for log in logs:
        command = f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{json.dumps(log)}\''
        print(f"\nSending log with command: {command}")
        subprocess.run(command, shell=True)