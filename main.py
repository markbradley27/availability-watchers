from absl import app
from absl import flags
from absl import logging
import notifiers
import pprint
import pyjokes
from typing import Dict, Text
import yaml

from watchers import base_watcher
from watchers.checkfront import gmc_huts, vt_huts
from util.date_range import DateRange

FLAGS = flags.FLAGS

flags.DEFINE_string("config_file", "./config.yaml", "Path to config file.")


def notify(subject, message, to_email, from_email, from_password):
  gmail = notifiers.get_notifier("gmail")
  gmail.notify(
      to=to_email,
      subject=subject,
      message=message,
      username=from_email,
      password=from_password,
      html=True)


def notify_diffs(diffs, to_email, from_email, from_password):
  #  doc, tag, text, line = yattag.Doc().ttl()
  #
  #  with tag('html'):
  #    with tag('body'):
  #      for provider, id_dict in diffs.items():
  #        line('h2', provider, style="margin: 0px 0px 0px 0px")
  #        for id, dates_dict in id_dict.items():
  #          line('h3', id, style="margin: 0px 0px 0px 20px")
  #          for date, newly_available in dates_dict.items():
  #            with tag('div', style="margin: 0px 0px 0px 40px"):
  #              text("{}: {}".format(
  #                  date, "Newly Available"
  #                  if newly_available else "Newly Unavailable"))
  #
  #  notify("AvailabilityWatcher found a diff!", doc.getvalue(), to_email,
  #         from_email, from_password)
  notify("AvailabilityWatcher found a diff!", pprint.pformat(diffs), to_email,
         from_email, from_password)


def notify_joke(to_email, from_email, from_password):
  logging.info("Just checking in (hope you like the joke!).")
  notify("AvailibilityWatcher just checking in.", pyjokes.get_joke(), to_email,
         from_email, from_password)


def main(argv):
  del argv

  with open(FLAGS.config_file, "r") as config_file:
    config = yaml.safe_load(config_file)
  logging.info("Config:\n%s", pprint.pformat(config))

  if (config["just_send_a_joke"]):
    return notify_joke(config["notify_email"], config["notifier_email"],
                       config["notifier_password"])

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
          date_range = DateRange(config_date_range["start_date"],
                                 config_date_range["end_date"])
          logging.info("Checking date range: %s", date_range)
          watcher_diffs = watcher.get_diffs(
              date_range, alert_group["providers"][watcher_name] or None)
          if watcher_diffs:
            diffs[watcher_name] = watcher_diffs

    if diffs:
      logging.info("Found diffs:\n%s", pprint.pformat(diffs))
      for alert_email in alert_group["emails"]:
        logging.info("Notifying: %s", alert_email)
        notify_diffs(diffs, alert_email, config["notifier_email"],
                     config["notifier_password"])
    else:
      logging.info("No diffs found.")


if __name__ == "__main__":
  app.run(main)
