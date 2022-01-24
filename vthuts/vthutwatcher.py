from absl import app
from absl import flags
from absl import logging

from email.message import EmailMessage
import json
import smtplib
import ssl
import urllib.request

FLAGS = flags.FLAGS

flags.DEFINE_string("notify_email", "", "Email address to notify.")
flags.DEFINE_string("notifier_email", "", "Account to send emails from.")
flags.DEFINE_string("notifier_password", "", "Password for notifier account.")

BASE_URL = "https://vermonthuts.checkfront.com/reserve/api/?call=calendar_days&start_date=2022-01-18&end_date=2022-03-01&category_id={category_id}&filter_category_id={filter_category_id}&filter_item_id={filter_item_id}"

CABINS = {
    42: "Dark Star Cabin",
    41: "Spikehorn Yurt",
    40: "Butternut Cabin",
    6: "Crow's Nest Yurt",
    4: "Triple Creek Cabin",
    2: "Nulhegan Hut",
    1: "Chittenden Brooke Hut",
}


def openings_filename(cabin_id):
  return "{}_openings.json".format(cabin_id)


def load_openings(cabin_id):
  try:
    with open(openings_filename(cabin_id), "r") as openings_file:
      return json.loads(openings_file.read())
  except FileNotFoundError:
    return {}


def fetch_openings(cabin_id):
  cabin_url = BASE_URL.format(
      category_id=cabin_id,
      filter_category_id=cabin_id,
      filter_item_id=cabin_id)
  with urllib.request.urlopen(cabin_url) as openings_url:
    return json.loads(openings_url.read().decode())


def save_openings(cabin_id, openings):
  with open(openings_filename(cabin_id), "w") as openings_file:
    openings_file.write(json.dumps(openings))


def diff_openings(saved, fetched):
  diffs = []
  for date in saved.keys():
    if saved[date] != fetched[date]:
      diffs.append(date)
  return diffs


def notify_of_diffs(diffs, to_email, from_email, from_password):
  msg = EmailMessage()
  content = "\n".join([
      "{} diffs: {}".format(CABINS[cabin_id], dates)
      for cabin_id, dates in diffs.items()
  ])
  msg.set_content(content)
  msg['Subject'] = "VTCabinWatcher found a diff!"
  msg['From'] = from_email
  msg['To'] = to_email

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(from_email, from_password)
    server.send_message(msg)


def main(argv):
  del argv

  diffs = {}
  for cabin_id in CABINS.keys():
    saved_openings = load_openings(cabin_id)
    fetched_openings = fetch_openings(cabin_id)
    cabin_diffs = diff_openings(saved_openings, fetched_openings)
    logging.debug("%s diffs: %s", CABINS[cabin_id], cabin_diffs)
    if cabin_diffs:
      diffs[cabin_id] = cabin_diffs
    save_openings(cabin_id, fetched_openings)

  if diffs:
    logging.info("Found diffs: %s", diffs)
    notify_of_diffs(diffs, FLAGS.notify_email, FLAGS.notifier_email,
                    FLAGS.notifier_password)
  else:
    logging.info("No diffs found.")


if __name__ == "__main__":
  app.run(main)
