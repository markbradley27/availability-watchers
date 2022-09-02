import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from typing import Dict, Text
import yattag

from watchers.base_watcher import AvailabilityDiffMap


class Notifier:
  SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

  def __init__(self, from_email: Text):
    self._from_email = from_email

    creds = None
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", self.SCOPES)
        creds = flow.run_local_server(port=0)
      with open("token.json", "w") as token:
        token.write(creds.to_json())

    self._service = build("gmail", "v1", credentials=creds)

  def send_email(self, to: Text, subject: Text, content: Text):
    message = MIMEText(content, "html")
    message["To"] = to
    message["From"] = self._from_email
    message["Subject"] = subject

    create_message = {
        "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
    }
    self._service.users().messages().send(
        userId="me", body=create_message).execute()

  def send_diffs(self, to: Text, diffs: Dict[Text, AvailabilityDiffMap]):
    doc, tag, text, line = yattag.Doc().ttl()

    with tag('html'):
      with tag('body'):
        for provider, date_dict in diffs.items():
          line('h2', provider, style="margin: 0px 0px 0px 0px")
          for date, site_dict in date_dict.items():
            line(
                'h3',
                date.strftime("%Y-%m-%d"),
                style="margin: 0px 0px 0px 20px")
            for site_id, availability_diff in site_dict.items():
              with tag('div', style="margin: 0px 0px 0px 40px"):
                text("{}: {} -> {}".format(
                    site_id, availability_diff.old if availability_diff.old
                    is not None else "?", availability_diff.new))
    self.send_email(to, "availability-watcher found a diff!", doc.getvalue())
