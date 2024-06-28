# python-halka-arz

This project is designed to track IPO (Initial Public Offering) announcements and send notifications to a specified Discord channel using web scraping techniques.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Disclaimer](#disclaimer)

## Introduction

python-halka-arz is a tool for monitoring IPO announcements and sending real-time notifications to a specified Discord channel. The application uses web scraping to gather the latest IPO data and automates the process of keeping users informed.

## Features

- **Web Scraping:** Automatically scrapes IPO information from relevant websites.
- **Discord Notifications:** Sends notifications to a specified Discord channel.
- **Automation:** Runs at regular intervals to ensure up-to-date information.

## Installation

To get started with Halka Arz Takip, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/burakozcn01/python-halka-arz.git
    cd python-halka-arz
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

## Usage

1. **Run the script:**
    ```sh
    python main.py
    ```

2. **Automate the script:** Use a task scheduler (e.g., cron job, Windows Task Scheduler) to run the script at regular intervals.

## Configuration

Before running the script, you need to configure the Discord webhook URL:

1. **Open `main.py`** and find the section where the Discord webhook URL is specified.
2. **Replace the placeholder URL with your actual Discord webhook URL:**
    ```python
    DISCORD_WEBHOOK_URL = "your_discord_webhook_url_here"
    ```

## Disclaimer

This project is intended for educational purposes only. Use it responsibly and at your own risk. The author is not responsible for any misuse of this tool.

---

If you have any questions or feedback, please feel free to open an issue or contact us.
