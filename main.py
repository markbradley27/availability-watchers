from absl import app
from absl import flags
from absl import logging
import notifiers
import pprint

import watchers

FLAGS = flags.FLAGS

flags.DEFINE_string("notify_email", "", "Email address to notify.")
flags.DEFINE_string("notifier_email", "", "Account to send emails from.")
flags.DEFINE_string("notifier_password", "", "Password for notifier account.")


def notify(diffs, to_email, from_email, from_password):
  gmail = notifiers.get_notifier("gmail")
  gmail.notify(
      to=to_email,
      subject="AvailabilityWatcher found a diff!",
      message=pprint.pformat(diffs),
      username=from_email,
      password=from_password)


def main(argv):
  del argv

  watcher_classes = (watchers.VTHutsWatcher,)

  diffs = {}
  for watcher_cls in watcher_classes:
    watcher = watcher_cls()
    watcher_diffs = watcher.get_diffs()
    if watcher_diffs:
      diffs[watcher_cls.NAME] = watcher_diffs

  if diffs:
    logging.info("Found diffs: %s", diffs)
    notify(diffs, FLAGS.notify_email, FLAGS.notifier_email,
           FLAGS.notifier_password)
  else:
    logging.info("No diffs found.")


if __name__ == "__main__":
  app.run(main)
