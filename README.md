# Gmail Bot Setup Instructions

This repository contains a Python bot that automatically responds to emails using the Gmail API and OpenAI's GPT.

## Prerequisites

- **Python 3.6+** installed on your system.
- **Google Cloud Account** with a project set up to use the Gmail API.
- **OpenAI API Key**.

## Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project

- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project or select an existing one.

### 1.2 Enable the Gmail API

- Navigate to the "APIs & Services" dashboard.
- Click on "Enable APIs and Services."
- Search for "Gmail API" and enable it for your project.

### 1.3 Create OAuth 2.0 Credentials

- Go to `APIs & Services` > `Credentials`.
- Click on "Create Credentials" and choose "OAuth 2.0 Client IDs."
- Set the application type to "Desktop app."
- Name your OAuth client ID (e.g., `Gmail Bot`).
- After creation, download the `credentials.json` file and place it in the directory where your bot scripts are located.

### 1.4 Set Authorized Redirect URI

- While creating the OAuth 2.0 credentials, add an authorized redirect URI.
- Set it to `http://localhost`.
- Save your changes.

## Step 2: Set Up Your Local Environment

### 2.1 Clone or Download the Project

- Place the `setup_gmail_bot.sh`, `config.env`, `email_bot.py`, and `credentials.json` in the same directory.

### 2.2 Add OpenAI API Key

- Open the `config.env` file and replace `your-openai-api-key-here` with your actual OpenAI API key.

### 2.3 Run the Setup Script

- Open a terminal and navigate to the directory containing the setup files.
- Make the setup script executable:

  ```bash
  chmod +x setup_gmail_bot.sh
