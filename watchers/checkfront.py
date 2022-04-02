import abc
from absl import logging
import datetime
import json
from typing import Dict, Text, Tuple
import urllib.request

from .abstract_watcher import AbstractWatcher, AvailabilityMap


class CheckFrontWatcher(AbstractWatcher):

  @property
  @abc.abstractmethod
  def base_url(self) -> Text:
    pass

  @property
  @abc.abstractmethod
  def cabins(self) -> Dict[Text, int]:
    pass

  @property
  def ids(self) -> Tuple[Text, ...]:
    return tuple(self.cabins)

  def fetch_availability(self, cabin_int: int, start_date: datetime.date,
                         end_date: datetime.date) -> AvailabilityMap:
    cabin_url = self.base_url.format(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        category_id=cabin_int,
        filter_category_id=cabin_int,
        filter_item_id=cabin_int)
    with urllib.request.urlopen(cabin_url) as openings_url:
      raw = json.loads(openings_url.read().decode())
      return {
          datetime.datetime.strptime(k, "%Y%m%d").date(): bool(v)
          for k, v in raw.items()
      }

  def get_diffs(self, start_date: datetime.date,
                end_date: datetime.date) -> Dict[Text, AvailabilityMap]:
    diffs = {}
    for cabin_id, cabin_int in self.cabins.items():
      logging.info("Checking %s.", cabin_id)
      saved = self.load_availability(cabin_id)
      fetched = self.fetch_availability(cabin_int, start_date, end_date)
      cabin_diffs = self.diff_availability(saved, fetched)

      if cabin_diffs:
        logging.info("Found diffs!")
        diffs[cabin_id] = cabin_diffs

      self.save_availability(fetched, cabin_id)

    return diffs
