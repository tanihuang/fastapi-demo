from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
import base64
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_creds():
  token_path = os.getenv("TOKEN_FILE")
  client_secret_path = os.getenv("CLIENT_SECRET_FILE")
  creds = None
  if os.path.exists(token_path):
      creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  if not creds or not creds.valid:
      flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
      creds = flow.run_local_server(port=0)
      with open(token_path, 'w') as token:
          token.write(creds.to_json())
  return creds

async def send_stock_alert(email_to: list[str], subject: str, context: dict):
  template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
  template_env = Environment(loader=FileSystemLoader(template_dir))
  template = template_env.get_template("stock_alert.html")
  html_content = template.render(context)

  message = MIMEText(html_content, "html")
  message["to"] = ",".join(email_to)
  message["subject"] = subject
  raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

  creds = get_gmail_creds()
  service = build("gmail", "v1", credentials=creds)
  result = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

  print(f"Email sent: ID = {result['id']}")
