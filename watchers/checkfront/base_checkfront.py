import abc
import datetime
import json
from typing import Dict, List, Optional, Text
import urllib.request

from util.date_range import DateRange
from watchers import base_watcher


class BaseCheckfront(base_watcher.BaseWatcher):

  @property
  @abc.abstractmethod
  def url_template(self) -> Text:
    """The url template to populate for each request."""
    pass

  @property
  @abc.abstractmethod
  def site_id_to_num_id(self) -> Dict[base_watcher.SiteId, int]:
    """Maps the site id used by this watcher to the number id used by
    checkfront."""
    pass

  @property
  def site_ids(self) -> List[base_watcher.SiteId]:
    return [k for k in self.site_id_to_num_id.keys()]

  def _fetch_availability(self,
                          date_range: DateRange,
                          site_ids: Optional[List[base_watcher.SiteId]] = None):
    for site_id in site_ids or self.site_ids:
      url = self.url_template.format(
          start_date=date_range.begin.strftime("%Y-%m-%d"),
          end_date=date_range.end.strftime("%Y-%m-%d"),
          category_id=self.site_id_to_num_id[site_id],
          filter_category_id=self.site_id_to_num_id[site_id],
          filter_item_id=self.site_id_to_num_id[site_id])
      with urllib.request.urlopen(url) as req:
        raw = json.loads(req.read().decode())
        parsed = {
            datetime.datetime.strptime(k, "%Y%m%d").date(): v
            for k, v in raw.items()
        }

        # Iterating through the provided date range will ensure an error is
        # thrown if the response is missing any dates.
        for date in date_range:
          self._cache.setdefault(date, {})[site_id] = parsed[date]
