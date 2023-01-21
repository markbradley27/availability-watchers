from absl import logging
from email.mime.text import MIMEText
import mailjet_rest
import os
from typing import Dict, Text
import yattag

from watchers.base_watcher import AvailabilityDiffMap


class Notifier:
  SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

  def __init__(self, from_email: Text):
    self._from_email = from_email

    self._mailjet = mailjet_rest.Client(
        auth=(os.environ["MJ_APIKEY_PUBLIC"], os.environ["MJ_APIKEY_PRIVATE"]),
        version="v3.1")

  def send_email(self, to: Text, subject: Text, content: Text):
    message = MIMEText(content, "html")
    message["To"] = to
    message["From"] = self._from_email
    message["Subject"] = subject
    data = {
        "Messages": [{
            "From": {
                "Email": self._from_email,
            },
            "To": [{
                "Email": to,
            },],
            "Subject": subject,
            "HTMLPart": content,
        },]
    }
    logging.info("data: %r", data)

    res = self._mailjet.send.create(data=data)
    res.raise_for_status()

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
