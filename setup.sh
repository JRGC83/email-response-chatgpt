#!/bin/bash

# Define the name of your virtual environment
VENV_NAME="gmail_bot_env"

# Step 1: Create the virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV_NAME

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Step 3: Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install required Python packages
echo "Installing required Python packages..."
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib openai schedule python-dotenv

# Step 5: Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "Error: credentials.json not found. Please place your credentials.json file in the current directory."
    deactivate
    exit 1
fi

# Step 6: Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "Error: config.env not found. Please create a config.env file with your OpenAI API key."
    deactivate
    exit 1
fi

# Step 7: Ensure that credentials.json is correct
echo "Checking credentials.json..."
if grep -q '"client_id"' "credentials.json"; then
    echo "credentials.json looks correct."
else
    echo "Error: credentials.json does not seem to be valid. Please ensure it is correctly formatted."
    deactivate
    exit 1
fi

# Step 8: Check if email_bot.py exists
if [ ! -f "email_bot.py" ]; then
    echo "Error: email_bot.py not found. Please place your email_bot.py script in the current directory."
    deactivate
    exit 1
fi

# Step 9: Notify user of next steps
echo "Setup complete. To run the Gmail bot, activate the virtual environment and execute the script:"
echo "source $VENV_NAME/bin/activate"
echo "python email_bot.py"

# Deactivate the virtual environment
deactivate

echo "Virtual environment deactivated. You can activate it later using 'source $VENV_NAME/bin/activate'."
