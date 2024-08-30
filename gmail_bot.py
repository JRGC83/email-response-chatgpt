import os
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

# Load environment variables from the config.env file
load_dotenv(dotenv_path="config.env")

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send']

# Functional approach: Helper functions
def load_credentials():
    """Load or refresh Gmail API credentials."""
    if os.path.exists('token.json'):
        return Credentials.from_authorized_user_file('token.json', SCOPES)
    return None

def refresh_credentials(creds):
    """Refresh credentials if needed."""
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def save_credentials(creds):
    """Save credentials to token.json."""
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def authenticate_gmail():
    """Authenticate Gmail API using credentials."""
    creds = load_credentials() or refresh_credentials(None)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        save_credentials(creds)
    return creds

def build_gmail_service(creds):
    """Build the Gmail service object."""
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_messages(service):
    """Fetch unread messages from Gmail."""
    response = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    return response.get('messages', [])

def get_message_details(service, message_id):
    """Fetch detailed message information."""
    return service.users().messages().get(userId='me', id=message_id).execute()

def parse_email_content(message):
    """Extract email content, such as subject and sender."""
    headers = message['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    snippet = message['snippet']
    return subject, sender, snippet

def generate_chatgpt_reply(snippet):
    """Generate a reply using ChatGPT based on the email snippet."""
    prompt = f"Reply to the following email:\n\n{snippet}\n\nResponse:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an email assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    return response['choices'][0]['message']['content']

def craft_reply_email(subject, sender, thread_id, reply_text):
    """Craft the MIMEText reply email."""
    message_body = MIMEText(reply_text)
    message_body['to'] = sender
    message_body['subject'] = f"Re: {subject}"
    message_body['threadId'] = thread_id
    raw_message = base64.urlsafe_b64encode(message_body.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_reply(service, reply_email):
    """Send the crafted reply email."""
    service.users().messages().send(userId='me', body=reply_email).execute()

def should_respond_to(sender):
    """Check if the email should be responded to based on the sender's address."""
    return sender.lower() == ""

def process_message(service, message):
    """Process each unread message."""
    message_details = get_message_details(service, message['id'])
    subject, sender, snippet = parse_email_content(message_details)
    
    if should_respond_to(sender):
        reply_text = generate_chatgpt_reply(snippet)
        reply_email = craft_reply_email(subject, sender, message_details['threadId'], reply_text)
        send_reply(service, reply_email)

def check_and_respond(service):
    """Check for unread messages and respond."""
    messages = fetch_unread_messages(service)
    if messages:
        for message in messages:
            process_message(service, message)

def main():
    creds = authenticate_gmail()
    service = build_gmail_service(creds)
    
    schedule.every(10).minutes.do(check_and_respond, service=service)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
