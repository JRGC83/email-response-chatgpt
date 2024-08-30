# Gmail Bot Setup Instructions

This repository contains a Python bot that automatically responds to emails using the Gmail API and OpenAI's GPT.

## Prerequisites

- **Python 3.6+** installed on your system.
- **Google Cloud Account** with a project set up to use the Gmail API.
- **OpenAI API Key**.
- **Homebrew** (optional, for managing packages like OpenSSL on macOS).

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

- While creating the OAuth 2.0 credentials, add an authorized redirect URI. You need to include the specific port number that will be used by your local server.
  - Example: `http://localhost:8080`.
- If your app is in testing mode (especially with "External" user type), ensure that the email address used for testing is added under the "Test users" section.
- Save your changes.

## Step 2: Set Up Your Local Environment

### 2.1 Clone or Download the Project

- Place the `setup_gmail_bot.sh`, `config.env`, `email_bot.py`, and `credentials.json` in the same directory.

### 2.2 Add OpenAI API Key and Whitelist Emails

- Open the `config.env` file and replace `your-openai-api-key-here` with your actual OpenAI API key.
- Add the email addresses that should receive automated responses, separated by commas.

Example `config.env`:

```env
OPENAI_API_KEY=your-openai-api-key-here
WHITELIST_EMAILS=justincrompton@msn.com,anotheremail@example.com
```

### 2.3 Run the Setup Script

- Open a terminal and navigate to the directory containing the setup files.
- Make the setup script executable:
  ```bash
  chmod +x setup_gmail_bot.sh
  ```
- Run the script:
  ```bash
  ./setup_gmail_bot.sh
  ```

### 2.4 Follow the Instructions

- The script will create a Python virtual environment, install the required dependencies, and check for necessary files.
- If the `credentials.json` or `config.env` files are missing or incorrect, the script will notify you.

## Step 3: Run the Gmail Bot

### 3.1 Activate the Virtual Environment

- After running the setup script, activate the virtual environment:
  ```bash
  source gmail_bot_env/bin/activate
  ```

### 3.2 Run the Gmail Bot

- Execute the Gmail bot script:
  ```bash
  python email_bot.py
  ```

### 3.3 Authenticate with Google

- The first time you run the script, a browser window will open asking you to sign in with your Google account and authorize access to your Gmail.
- After successful authentication, a `token.json` file will be created, allowing the script to access your Gmail account without needing to sign in again.

## Handling SSL Issues

If you encounter SSL-related warnings or errors, such as:

```
/Users/username/gmail_bot_env/lib/python3.9/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'.
```

### Solution Options:

1. **Downgrade `urllib3`**:
   ```bash
   pip install 'urllib3<2'
   ```

2. **Manually Update OpenSSL** (if necessary):
   - Install OpenSSL via Homebrew:
     ```bash
     brew install openssl
     ```
   - Recompile Python to use the updated OpenSSL (advanced users).

## Troubleshooting

- **OAuth Error**: If you encounter an error during Google authentication, ensure that your redirect URI is set correctly to `http://localhost:8080` or another specific port in the Google Cloud Console, and that your email is added as a test user if in testing mode.
- **Missing Packages**: If any required Python packages are not found, make sure they are installed in your virtual environment by rerunning the setup script.

## Additional Notes

- **Token File**: The `token.json` file generated during authentication stores your credentials securely. Do not share this file.
- **Re-authentication**: If you need to re-authenticate or change the Google account, delete the `token.json` file and rerun the script.

---

By following this guide, you should be able to set up and run the Gmail bot successfully. Let me know if you need any more help!
