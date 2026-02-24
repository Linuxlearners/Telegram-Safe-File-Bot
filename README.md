# Telegram Safe File Bot

A secure, GUI-based Telegram file sharing bot built using Python, Tkinter, and python-telegram-bot.  
The application enables controlled file distribution from a selected local directory through Telegram with pagination, access control, and safe directory traversal protections.

---

## Overview

Telegram Safe File Bot allows users to browse and download files from a predefined local folder using an interactive inline keyboard interface inside Telegram. The application includes a graphical control panel for configuration and supports both public and restricted access modes.

This project is designed with security, usability, and safe resource handling in mind.

---

## Key Features

- Interactive folder navigation using Telegram inline keyboards
- File download support (up to 50MB per file)
- Public or Private access mode
- Custom authorized user ID restriction
- Safe directory tree preview with depth limitation
- Pagination for large directories
- Message length protection (Telegram-safe limits)
- GUI-based configuration panel
- Threaded bot execution
- Timeout handling for large file uploads

---

## Security Controls

- Authorized user access restriction (Custom mode)
- Maximum file size enforcement (50MB limit)
- Safe directory tree depth control
- Line limit protection for directory preview
- Telegram message size protection
- UUID-based file mapping per user session
- Prevention of uncontrolled directory traversal

---

## Project Structure

```

Telegram-Safe-File-Bot/
│
├── README.md
├── filesharebot.py
├── requirements.txt
└── screenshots/

````

---

## Requirements

- Python 3.9+
- python-telegram-bot (v20+)

Install dependencies:

```bash
pip install -r requirements.txt
````

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/Telegram-Safe-File-Bot.git
cd Telegram-Safe-File-Bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python filesharebot.py
```

---

## Configuration

The application provides both GUI-based configuration and persistent default configuration inside the source code.

### GUI Configuration

* Enter Bot Token
* Select Security Mode (Public / Private)
* Provide Authorized User IDs (if Private mode)
* Select Shared Folder
* Start the bot

### Persistent Default Configuration

For repetitive deployments or personal use, default values can be predefined inside the source code:

```python
DEFAULT_BOT_TOKEN = "YOUR_BOT_TOKEN"
DEFAULT_ADMIN_IDS = "123456789"
DEFAULT_SECURITY_MODE = "Custom"
```

This allows:

* Rapid repeated usage without manual re-entry
* Pre-configured admin access
* Permanent private mode setup
* Faster deployment in controlled environments

When modified, these values are automatically loaded into the GUI on startup.

---

## How It Works

1. The bot initializes using python-telegram-bot with async polling.
2. A safe directory tree preview is generated with depth and line limits.
3. Inline keyboards are dynamically generated with UUID-based mapping.
4. Users navigate directories through callback queries.
5. File uploads are validated against size limits before transmission.
6. Access control is enforced based on selected security mode.

---

## Use Cases

* Secure personal file distribution
* Internal document sharing
* Lightweight local file management via Telegram
* Controlled private file access for small teams

---

## Future Improvements

* File upload support
* Search functionality
* Logging and audit trail system
* Docker containerization
* Web-based dashboard
* Role-based access control

---

## Technical Highlights

* Asynchronous bot handling with asyncio
* Threaded execution to prevent GUI blocking
* Pagination logic for scalable directory browsing
* Controlled recursion for safe file tree rendering
* Per-user file mapping to prevent ID collisions

---

## License

This project is intended for educational and controlled usage purposes.

---

## Project Status

This project is currently released as a pilot implementation focused on secure navigation, controlled access, and safe file sharing using the Telegram Bot API.

At present, file transfers are limited to **50MB per file**, in accordance with the default Telegram cloud Bot API limitations.

Support for larger file transfers (up to **2GB per file**) via a self-hosted Local Bot API Server is planned for a future release.

---

## File Size Limitation

By default, bots running on Telegram’s cloud infrastructure are restricted to 50MB per file.

To enable file transfers up to 2GB, the bot must be configured to use Telegram’s official self-hosted Bot API Server. This requires:

1. Deploying the Telegram Bot API Server on a dedicated machine with sufficient storage and bandwidth.
2. Configuring the bot to communicate with the local server endpoint instead of the default cloud endpoint.
3. Managing file uploads and downloads directly through the local environment.

Local Bot API integration is currently under development and will be available in an upcoming release.

---

<p align="center">
  <sub>Bot by Kamal Varma</sub>
</p>

<p align="center">
  <a href="https://medium.com/@Linuxlearners" target="_blank">
    <img src="https://img.shields.io/badge/Medium-Connect-black?logo=medium&logoColor=white" alt="Connect on Medium" />
  </a>
</p>


