# Zscaler Log Generator

## Overview

Welcome to the Zscaler Log Generator, a powerful tool designed to generate realistic Zscaler log data for testing and analysis. This tool allows you to create detailed logs that simulate user interactions and network traffic in a Zscaler environment, helping you validate and analyze log data in NGSIEM or other log management systems.

## Features

- Generate Zscaler web, firewall, DNS, and CASB logs
- Simulate user interactions with realistic data
- Configurable through an intuitive menu system
- Send generated logs to NGSIEM or other log management APIs

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
    pip install -r requirements.txt
    ```

## Usage

Run the script through the menu system. Execute the `menu.py` script, and it will guide you through the various functionalities.

```bash
python3 menu.py
```

### Configuration

Customize your experience by editing the config.json file. Add new data sources, tweak parameters, and make the scripts work for your specific needs.

## 🎓 About this Project

This project was created to aid in the learning and testing of log data ingestion and analysis in Zscaler environments. It’s a valuable tool for incident responders, security analysts, and anyone looking to understand and work with Zscaler log data.

### Authors

- Jack Turner - Senior Instructor at CrowdStrike - LinkedIn

### Contact

For contact or support, reach out via LinkedIn or open an issue on this repository.

### License

This project is licensed under the Apache-2.0 License. See the LICENSE file for details.

### Contributing

Feel free to fork this repository, make your changes, and submit a pull request. Contributions are welcome!

## References

For more information about Zscaler logs and data ingestion, visit the Zscaler Documentation.