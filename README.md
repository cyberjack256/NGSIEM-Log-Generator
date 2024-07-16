# Zscaler Log Generator

This project generates sample logs that can be sent to NGSIEM (Next-Generation Security Information and Event Management) using a configurable set of parameters. The generated logs simulate web traffic and can be used for testing and validation purposes.

## About This Project

The Zscaler Log Generator is designed to help users simulate realistic log data for testing and analysis. This project is particularly useful for security analysts and developers working with NGSIEM platforms. The logs generated follow a predefined format to ensure compatibility with Zscaler's logging systems.

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/cyberjack256/Traffic.git
```
2. **Navigate to the project directory:**
```bash
   cd Traffic
```

3. **Install the required libraries:**
```bash
   pip3 install -r requirements.txt
```

## Configuration

Create a `config.yaml` file with the necessary configuration values. Below is an example configuration:
```yaml
api_url: "https://your-ngsiem-api-url"
api_key: "your_api_key"

usernames:
  - sparrow
  - robin
  - eagle

mac_addresses:
  - 00:1A:2B:3C:4D:5E
  - 11:22:33:44:55:66

user_agents:
  - Mozilla/5.0
  - Chrome/91.0

server_ips:
  - 192.168.1.1
  - 192.168.1.2

client_ips:
  - 10.0.0.1
  - 10.0.0.2

hostnames:
  - birdserver.example.com
  - eaglehost.example.com
```
## Usage

Run the menu script to interactively configure and generate logs:
```bash
python menu.py
```
Follow the on-screen instructions to add configuration values and generate logs.

## Requirements

Create a `requirements.txt` file with the following content:
```text
requests
json
datetime
logging
pyyaml
faker
pytz
random
```
## Contact and Support

For support, reach out via [LinkedIn](https://www.linkedin.com/in/cyberjack256) or open an issue on this repository. GitHub responses are preferred for this project.

## Authors

- Jack Turner - [cyberjack256](https://www.linkedin.com/in/cyberjack256)

## License

This project is licensed under the Apache-2.0 License. See the LICENSE file for details.