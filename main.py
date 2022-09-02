from absl import app
from absl import flags
from absl import logging
import datetime
import pprint
import pyjokes
from typing import Dict, Text
import yaml

from watchers import base_watcher
from watchers.checkfront import gmc_huts, vt_huts
from util.date_range import DateRange
from util.notifier import Notifier

FLAGS = flags.FLAGS

flags.DEFINE_string("config_file", "./config.yaml", "Path to config file.")


def main(argv):
  del argv

  with open(FLAGS.config_file, "r") as config_file:
    config = yaml.safe_load(config_file)
  logging.info("Config:\n%s", pprint.pformat(config))

  notifier = Notifier(config["notifier_email"])

  if "just_send_a_joke_to" in config:
    notifier.send_email(config["just_send_a_joke_to"],
                        "availability-watcher just checking in",
                        pyjokes.get_joke())
    return

  watchers = (gmc_huts.GMCHuts(), vt_huts.VTHuts())

  # TODO: Notify if anything goes wrong.
  for alert_group in config["alert_groups"]:
    logging.info("Handling alert group:\n%s", pprint.pformat(alert_group))
    diffs: Dict[Text, base_watcher.AvailabilityDiffMap] = {}
    for watcher in watchers:
      watcher_name = type(watcher).__name__
      if watcher_name in alert_group["providers"]:
        logging.info("Checking watcher: %s", watcher_name)
        for config_date_range in alert_group["date_ranges"]:
          start_date = config_date_range["start_date"]
          if start_date < datetime.date.today():
            start_date = datetime.date.today()
          date_range = DateRange(start_date, config_date_range["end_date"])
          logging.info("Checking date range: %s", date_range)
          watcher_diffs = watcher.get_diffs(
              date_range, alert_group["providers"][watcher_name] or None)
          if watcher_diffs:
            diffs[watcher_name] = watcher_diffs

    if diffs:
      logging.info("Found diffs:\n%s", pprint.pformat(diffs))
      for alert_email in alert_group["emails"]:
        logging.info("Notifying: %s", alert_email)
        notifier.send_diffs(alert_email, diffs)
    else:
      logging.info("No diffs found.")


if __name__ == "__main__":
  app.run(main)
