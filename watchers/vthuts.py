from absl import logging
import datetime
import json
from typing import Dict, Text
import urllib.request

from .abstract_watcher import AbstractWatcher, AvailabilityMap


class VTHutsWatcher(AbstractWatcher):

  NAME = "VTHuts"

  _BASE_URL = "https://vermonthuts.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id={category_id}&filter_category_id={filter_category_id}&filter_item_id={filter_item_id}"

  _CABINS = {
      42: "Dark Star Cabin",
      41: "Spikehorn Yurt",
      40: "Butternut Cabin",
      6: "Crow's Nest Yurt",
      4: "Triple Creek Cabin",
      2: "Nulhegan Hut",
      1: "Chittenden Brooke Hut",
  }

  def fetch_availability(self, cabin_id: int, start_date: datetime.date,
                         end_date: datetime.date) -> AvailabilityMap:
    cabin_url = self._BASE_URL.format(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        category_id=cabin_id,
        filter_category_id=cabin_id,
        filter_item_id=cabin_id)
    with urllib.request.urlopen(cabin_url) as openings_url:
      raw = json.loads(openings_url.read().decode())
      return {
          datetime.datetime.strptime(k, "%Y%m%d").date(): bool(v)
          for k, v in raw.items()
      }

  def get_diffs(self, start_date: datetime.date,
                end_date: datetime.date) -> Dict[Text, AvailabilityMap]:
    diffs = {}
    for cabin_id, cabin_name in self._CABINS.items():
      logging.info("Checking %s.", cabin_name)
      saved = self.load_availability(cabin_id)
      fetched = self.fetch_availability(cabin_id, start_date, end_date)
      cabin_diffs = self.diff_availability(saved, fetched)

      if cabin_diffs:
        logging.info("Found diffs!")
        diffs[cabin_name] = cabin_diffs

      self.save_availability(fetched, cabin_id)

    return diffs
