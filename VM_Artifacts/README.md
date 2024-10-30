# README #

## Welcome to the Next-Gen SIEM Log Generator!

This document provides a high-level overview of the SIEM 210 Next-Gen SIEM Log Generator application, its components, and how they interoperate. Whether you're a lab manager, instructor, or lay-person, this guide will help you understand the purpose of each part of the application and how to get started working with it.

## Table of Contents
- [Introduction](#introduction)
- [Application Overview](#application-overview)
- [Components](#components)
    - [menu.py](#menu-py)
    - [generate_logs.py](#generate-logs-py)
    - [generate_syslog_logs.py](#generate-syslog-logs-py)
    - [config.json](#config-json)
    - [message.config](#message-config)
- [Interoperability and Workflow](#interoperability-and-workflow)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Usage](#usage)
- [Function Documentation](#function-documentation)
    - [menu.py Functions](#menu-py-functions)
    - [generate_logs.py Functions](#generate-logs-py-functions)
    - [generate_syslog_logs.py Functions](#generate-syslog-logs-py-functions)
- [Important Notes](#important-notes)

## Introduction

The Next-Gen SIEM Log Generator is a tool designed to simulate various network activities by generating logs in formats compatible with CrowdStrike Falcon Next-Gen SIEM push connector, such as Zscaler and formats compatible with CrowdStrike LogScale LogCollector, such as syslog. It helps in testing, validating, and demonstrating SIEM configurations and detections by providing realistic and diverse log data.

## Application Overview

The application consists of scripts that generate logs mimicking real-world network traffic and events for a ficticious company. The logs can represent both normal operations and security incidents, allowing SIEM systems to process and analyze them as if they were live data.

### Main Components
- **Menu Interface (menu.py):** A command-line menu for configuration, settings management, and service control.
- **Log Generators:**
    - **Zscaler Log Generator (generate_logs.py):** Simulates web traffic logs in Zscaler's format.
    - **Syslog Log Generator (generate_syslog_logs.py):** Generates syslog messages using predefined templates.
- **Configuration Files:**
    - **config.json:** Contains configurations and data for the log generators.
    - **message.config:** Holds syslog message templates.

## Components

### menu.py

`menu.py` is the central interface of the application. It provides a text-based menu that allows users to:

- Configure settings for Zscaler logs, syslog messages, and the Falcon LogScale LogCollector.
- Start and stop log generation services.
- View and edit configurations.
- Manage the inclusion of debug logs.

**Key Features:**

- User-friendly navigation.
- Real-time updates and feedback.
- Integration with other components for seamless operation.

### generate_logs.py

This script generates logs in Zscaler's Nanolog Streaming Service (NSS) format, simulating:
- **Regular Traffic Logs:** Normal user behavior.
- **Malicious Traffic Logs:** Access to known malicious URLs or suspicious actions.

**How It Works:**

- Loads data from `config.json`.
- Generates log entries with dynamic data (e.g., timestamps, URLs, IP addresses).
- Sends logs to a configured API endpoint using HTTP requests.

### generate_syslog_logs.py

This script generates syslog messages based on templates in `message.config`. It can:

- Create logs of different severity levels (info, warning, error, etc.).
- Send logs to a syslog server over UDP.
- Run continuously as a service.

**Key Features:**

- Uses dynamic data to create realistic logs.
- Adjustable log generation rate.
- Status monitoring for the log-sending process.

### config.json

`config.json` contains configuration data, such as:

- Simulated users, malicious entities, and network connections.
- Templates for drone data, network attacks, and API settings.

### message.config

A JSON file that holds syslog message templates organized by severity levels. Placeholders within templates are filled dynamically during log generation.

## Interoperability and Workflow

- **Configuration Loading:** All scripts load settings from `config.json` and `message.config` to ensure consistency.
- **Menu Interaction:** `menu.py` allows users to configure settings and manage log generation.
- **Log Generation:** Depending on user actions, the scripts create logs using dynamic data.
- **Log Transmission:** Logs are sent to configured endpoints, such as APIs for Zscaler logs or UDP for syslog.
- **Service Management:** Log generation can run as background services, managed via `menu.py`.

## Getting Started

### Prerequisites
- **Python Version:** Python 3.6 or higher
- **Required Packages:** Listed in `requirements.txt`
  - Install with: 

pip install -r requirements.txt

### Installation
1. **Clone the Repository:** 
```bash
git clone <repository-url>
cd NGSIEM-Log-Generator
```

2. **Install Dependencies:** 

```bash
pip install -r requirements.txt
```

3. **Set Up Configuration Files:**
- Update `config.json` with environment details.
- Ensure `message.config` is present in the directory.

### Configuration
- **Update config.json:** Input realistic data for users, malicious entities, and API settings.
- **Set API Endpoints and Keys:** Replace placeholders with actual values.
- **Define Observer ID:** Set a unique identifier for your instance.

### Usage
- **Run the Menu Interface:**

```bash
python menu.py
```
## Function Documentation

### menu.py Functions
- **main_menu():** Presents the main menu.
- **zscaler_menu():** Manages Zscaler log actions.
- **syslog_menu():** Manages syslog log actions.
- **load_config():** Loads configuration data from `config.json`.
- **start_logging_service():** Starts the log generation service.

### generate_logs.py Functions
- **generate_zscaler_log(...):** Creates Zscaler-formatted log entries.
- **run_as_service(config):** Continuously generates and sends logs.

### generate_syslog_logs.py Functions
- **generate_sample_syslogs():** Generates sample syslog messages.
- **start_send_to_syslog_service():** Starts syslog message service.

## Important Notes