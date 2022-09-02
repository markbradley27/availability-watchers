import abc
import datetime
import json
from typing import Dict, List, Optional, Text
import urllib.request

from util.date_range import DateRange
from watchers.base_watcher import BaseWatcher, SiteId


class BaseRecreationGov(BaseWatcher):
  URL_TEMPLATE = "https://www.recreation.gov/api/camps/availability/campground/{campground_id}/month?start_date={start_date}T00%3A00%3A00.000Z"

  @property
  @abc.abstractmethod
  def campground_id(self) -> Text:
    pass

  @property
  @abc.abstractmethod
  def rec_id_to_site_id(self) -> Dict[Text, SiteId]:
    pass

  @property
  def site_ids(self) -> List[SiteId]:
    return [v for v in self.rec_id_to_site_id.values()]

  def _fetch_availability(self,
                          date_range: DateRange,
                          site_ids: Optional[List[SiteId]] = None):
    # Recreation.gov API gives you a month of info at a time, and all start
    # dates must be the first of the month.
    start_date = datetime.date(date_range.begin.year, date_range.begin.month, 1)

    site_ids = site_ids if site_ids is not None else self.site_ids

    while start_date <= date_range.end:
      url = self.URL_TEMPLATE.format(
          campground_id=self.campground_id, start_date=start_date.isoformat())
      with urllib.request.urlopen(url) as req:
        raw = json.loads(req.read().decode())

        for rec_id, site_info in raw["campsites"].items():
          if rec_id in self.rec_id_to_site_id and self.rec_id_to_site_id[
              rec_id] in site_ids:
            for iso_date, availability_str in site_info["availabilities"].items(
            ):
              if iso_date.endswith("Z"):
                iso_date = iso_date[:-1]
              date = datetime.datetime.fromisoformat(iso_date).date()
              availability = 1 if availability_str == "Available" else 0
              self._cache.setdefault(
                  date, {})[self.rec_id_to_site_id[rec_id]] = availability

      start_date = datetime.date(
          start_date.year if start_date.month < 12 else start_date.year + 1,
          start_date.month + 1 if start_date.month < 12 else 1, 1)
