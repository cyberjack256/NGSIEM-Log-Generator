# Zscaler Log Generator

This project generates sample logs for Zscaler and sends them to an NGSIEM. It includes a menu-driven interface for configuring log parameters, generating sample logs, and sending logs to NGSIEM. It also supports setting up a cron job to send logs periodically.

## About This Project

The Zscaler Log Generator is designed to help security analysts and developers with testing and validation. It uses Faker to generate realistic log data based on predefined and configurable sets of parameters.

## Requirements

Create a `requirements.txt` file with the following content:
```txt
requests
json
datetime
logging
pytz
random
faker
```
## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Install the required libraries using pip:
   pip install -r requirements.txt

## Configuration

The configuration is stored in `config.json`. Here is an example of the configuration file:
```json
{
  "api_url": "https://your-ngsiem-api-url",
  "api_key": "your_api_key",
  "usernames": ["sparrow", "robin", "eagle"],
  "mac_addresses": ["00:1A:2B:3C:4D:5E", "11:22:33:44:55:66"],
  "user_agents": ["Mozilla/5.0", "Chrome/91.0"],
  "server_ips": ["192.168.1.1", "192.168.1.2"],
  "client_ips": ["10.0.0.1", "10.0.0.2"],
  "hostnames": ["birdserver.example.com", "eaglehost.example.com"]
}
```

## Usage

Run the menu script to interact with the log generator:
```bash
python3 menu.py
```
The menu options are:

1. Show current configuration
2. Add a configuration value
3. Clear a configuration value
4. Generate sample logs
5. Send logs to NGSIEM
6. View cron job
7. Set cron job
8. Delete cron job
0. Exit

## Contact and Support

For support, reach out via [LinkedIn](https://www.linkedin.com/in/cyberjack256) or open an issue on this repository. GitHub responses are preferred for this project.

## Authors

Jack Turner - [cyberjack256](https://github.com/cyberjack256)

## License

This project is licensed under the MIT License.