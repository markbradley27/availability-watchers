import abc
from absl import logging
from dataclasses import dataclass
import datetime
import json
from typing import Dict, List, Optional, Text

from util.date_range import DateRange


@dataclass
class AvailabilityDiff:
  old: Optional[int]
  new: Optional[int]


SiteId = Text
AvailabilityMap = Dict[datetime.date, Dict[SiteId, int]]
AvailabilityDiffMap = Dict[datetime.date, Dict[SiteId, AvailabilityDiff]]


class BaseWatcher(abc.ABC):
  _SAVED_DATE_FORMAT = "%Y-%m-%d"

  @property
  @abc.abstractmethod
  def site_ids(self) -> List[SiteId]:
    """List of all site IDs supported by this watcher. Should be numbers or
    lowercase underscore separated words."""
    pass

  @abc.abstractmethod
  def _fetch_availability(self,
                          date_range: DateRange,
                          site_ids: Optional[List[SiteId]] = None):
    """Fetches and populates _cache with availability counts for the given date
    ranges and site IDs."""
    pass

  @property
  def filename(self) -> Text:
    return "availability_files/{}_availability.json".format(type(self).__name__)

  def __init__(self):
    self._previous = self._load_previous_availability()
    self._cache: AvailabilityMap = {}

  def __del__(self):
    self._save_availability(self._cache)

  def _load_previous_availability(self) -> AvailabilityMap:
    try:
      with open(self.filename, "r") as file:
        formatted = json.loads(file.read())
        return {
            datetime.datetime.strptime(k, self._SAVED_DATE_FORMAT).date(): v
            for k, v in formatted.items()
        }
    except FileNotFoundError:
      return {}

  def _save_availability(self, availability: AvailabilityMap):
    with open(self.filename, "w") as file:
      formatted = {
          k.strftime(self._SAVED_DATE_FORMAT): v
          for k, v in availability.items()
      }
      file.write(json.dumps(formatted, sort_keys=True, indent=2))

  def _check_cache(self,
                   date_range: DateRange,
                   site_ids: Optional[List[SiteId]] = None) -> bool:
    """Returns true iff every date and site is present in the cache."""
    for date in date_range:
      if date not in self._cache:
        return False
      for site_id in (site_ids if site_ids is not None else self.site_ids):
        if site_id not in self._cache[date]:
          return False
    return True

  def get_diffs(self,
                date_range: DateRange,
                site_ids: Optional[List[SiteId]] = None) -> AvailabilityDiffMap:
    diff_map: AvailabilityDiffMap = {}

    # if availability for any site for any date in the range is missing from
    # the cache, fetch the whole date range (crude but effective)
    if not self._check_cache(date_range, site_ids):
      logging.info(
          "Fetching availability; watcher: %s, date_range: %s, site_ids: %s",
          type(self).__name__, date_range, site_ids)
      self._fetch_availability(date_range, site_ids)

    for date in date_range:
      for site_id in (site_ids if site_ids is not None else self.site_ids):
        potential_diff = AvailabilityDiff(
            self._previous.get(date, {}).get(site_id, None),
            self._cache[date][site_id])
        if potential_diff.old != potential_diff.new:
          diff_map.setdefault(date, {})[site_id] = potential_diff

    return diff_map
