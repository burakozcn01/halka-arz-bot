# Halka Arz Bot
A tool designed to track IPO (Initial Public Offering) announcements and send notifications to the terminal using web scraping techniques.

## 📌 Introduction
**Halka Arz Bot** is a utility for monitoring IPO announcements and delivering real-time updates to the terminal. It uses web scraping to fetch the latest IPO information, automating the process of keeping users informed.

---

## ✨ Features
- **Web Scraping**: Automatically gathers IPO data from relevant websites.
- **Terminal Notifications**: Sends timely alerts to the terminal.
- **Automation**: Operates at regular intervals to ensure the latest information is always available.

---

## ⚙️ Installation
Follow these steps to set up **Halka Arz Bot**:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/burakozcn01/halka-arz-bot.git
    cd halka-arz-bot
    ```

2. **Set up a virtual environment**:
    ```sh
    python3 -m venv env
    source env/bin/activate  # For Windows: `env\Scripts\activate`
    ```

3. **Install required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

---

## 🚀 Usage
1. **Run the script manually**:
    ```sh
    python main.py
    ```

2. **Automate the script**:
   - Use a task scheduler like **cron jobs** (Linux/macOS) or **Task Scheduler** (Windows) to execute the script at desired intervals.

---

## 🛠️ Configuration
Before running the script, ensure the correct configuration:

1. Open the `config.yaml` file.
2. Update the following fields in the configuration:
    ```yaml
    sent_halkarz_file: "sent_halkarz.json"
    scrape_url: "https://halkarz.com/"
    check_interval: 300  # 5 minutes
    ```

---

## ⚠️ Disclaimer
This project is for **educational purposes only**. Use it responsibly and in compliance with applicable laws. The creator is not liable for any misuse or potential issues caused by this tool.

---

For feedback, questions, or reporting issues, please open an issue on the repository or contact us.
