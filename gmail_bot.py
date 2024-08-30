import os
import logging
from dotenv import load_dotenv
import openai
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import schedule

# Set up logging
logging.basicConfig(filename='email.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Starting email bot...')

# Load environment variables from the config.env file
load_dotenv(dotenv_path="config.env")
logging.info('Loaded environment variables from config.env')

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
logging.info('OpenAI API key set.')

# Load whitelist emails from the environment variable
WHITELIST_EMAILS = os.getenv('WHITELIST_EMAILS').split(',')
logging.info(f'Whitelist emails loaded: {WHITELIST_EMAILS}')

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send']

# Functional approach: Helper functions
def load_credentials():
    """Load or refresh Gmail API credentials."""
    logging.info('Loading credentials...')
    if os.path.exists('token.json'):
        logging.info('Credentials found. Loading from token.json')
        return Credentials.from_authorized_user_file('token.json', SCOPES)
    logging.warning('Credentials not found. Proceeding with authentication.')
    return None

def refresh_credentials(creds):
    """Refresh credentials if needed."""
    if creds and creds.expired and creds.refresh_token:
        logging.info('Refreshing expired credentials...')
        creds.refresh(Request())
    else:
        logging.info('No need to refresh credentials.')
    return creds

def save_credentials(creds):
    """Save credentials to token.json."""
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    logging.info('Credentials saved to token.json')

def authenticate_gmail():
    """Authenticate Gmail API using credentials."""
    creds = load_credentials() or refresh_credentials(None)
    if not creds or not creds.valid:
        logging.info('Starting OAuth flow for Gmail API authentication...')
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='http://localhost')
        creds = flow.run_local_server(port=0)
        save_credentials(creds)
        logging.info('Authentication successful.')
    return creds

def build_gmail_service(creds):
    """Build the Gmail service object."""
    logging.info('Building Gmail service...')
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_messages(service):
    """Fetch unread messages from Gmail."""
    logging.info('Fetching unread messages...')
    response = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = response.get('messages', [])
    logging.info(f'Found {len(messages)} unread messages.')
    return messages

def get_message_details(service, message_id):
    """Fetch detailed message information."""
    logging.info(f'Fetching details for message ID: {message_id}')
    return service.users().messages().get(userId='me', id=message_id).execute()

def parse_email_content(message):
    """Extract email content, such as subject and sender."""
    headers = message['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    snippet = message['snippet']
    logging.info(f'Parsed email content: subject={subject}, sender={sender}')
    return subject, sender, snippet

def generate_chatgpt_reply(snippet):
    """Generate a reply using ChatGPT based on the email snippet."""
    logging.info('Generating reply using OpenAI ChatGPT...')
    prompt = f"Reply to the following email:\n\n{snippet}\n\nResponse:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an email assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    reply = response['choices'][0]['message']['content']
    logging.info('Generated reply: ' + reply)
    return reply

def craft_reply_email(subject, sender, thread_id, reply_text):
    """Craft the MIMEText reply email."""
    logging.info(f'Crafting reply email to: {sender}')
    message_body = MIMEText(reply_text)
    message_body['to'] = sender
    message_body['subject'] = f"Re: {subject}"
    message_body['threadId'] = thread_id
    raw_message = base64.urlsafe_b64encode(message_body.as_bytes()).decode('utf-8')
    logging.info('Reply email crafted.')
    return {'raw': raw_message}

def send_reply(service, reply_email):
    """Send the crafted reply email."""
    logging.info('Sending reply email...')
    service.users().messages().send(userId='me', body=reply_email).execute()
    logging.info('Reply email sent successfully.')

def should_respond_to(sender):
    """Check if the email should be responded to based on the sender's address."""
    should_respond = sender.lower() in [email.strip().lower() for email in WHITELIST_EMAILS]
    logging.info(f'Should respond to {sender}: {should_respond}')
    return should_respond

def process_message(service, message):
    """Process each unread message."""
    logging.info(f'Processing message ID: {message["id"]}')
    message_details = get_message_details(service, message['id'])
    subject, sender, snippet = parse_email_content(message_details)
    
    if should_respond_to(sender):
        reply_text = generate_chatgpt_reply(snippet)
        reply_email = craft_reply_email(subject, sender, message_details['threadId'], reply_text)
        send_reply(service, reply_email)
    else:
        logging.info(f'Skipping message from: {sender}')

def check_and_respond(service):
    """Check for unread messages and respond."""
    logging.info('Checking for unread messages...')
    messages = fetch_unread_messages(service)
    if messages:
        for message in messages:
            process_message(service, message)

def main():
    logging.info('Starting main function...')
    creds = authenticate_gmail()
    service = build_gmail_service(creds)
    
    schedule.every(10).minutes.do(check_and_respond, service=service)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
