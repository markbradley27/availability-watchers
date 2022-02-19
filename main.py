from absl import app
from absl import flags
from absl import logging
import notifiers
import pyjokes
import yaml
import yattag

import watchers

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
  doc, tag, text, line = yattag.Doc().ttl()

  with tag('html'):
    with tag('body'):
      for provider, id_dict in diffs.items():
        line('h2', provider, style="margin: 0px 0px 0px 0px")
        for id, dates_dict in id_dict.items():
          line('h3', id, style="margin: 0px 0px 0px 20px")
          for date, newly_available in dates_dict.items():
            with tag('div', style="margin: 0px 0px 0px 40px"):
              text("{}: {}".format(
                  date, "Newly Available"
                  if newly_available else "Newly Unavailable"))

  notify("AvailabilityWatcher found a diff!", doc.getvalue(), to_email,
         from_email, from_password)


def notify_joke(to_email, from_email, from_password):
  logging.info("Just checking in (hope you like the joke!).")
  notify("AvailibilityWatcher just checking in!", pyjokes.get_joke(), to_email,
         from_email, from_password)


def main(argv):
  del argv

  with open(FLAGS.config_file, "r") as config_file:
    config = yaml.safe_load(config_file)

  if (config["just_send_a_joke"]):
    return notify_joke(config["notify_email"], config["notifier_email"],
                       config["notifier_password"])

  watcher_classes = (watchers.GMCWatcher, watchers.VTHutsWatcher)

  diffs = {}
  for watcher_cls in watcher_classes:
    watcher = watcher_cls()
    watcher_diffs = watcher.get_diffs(config["start_date"], config["end_date"])
    if watcher_diffs:
      diffs[watcher_cls.NAME] = watcher_diffs

  if diffs:
    logging.info("Found diffs: %s", diffs)
    notify_diffs(diffs, config["notify_email"], config["notifier_email"],
                 config["notifier_password"])
  else:
    logging.info("No diffs found.")


if __name__ == "__main__":
  app.run(main)
