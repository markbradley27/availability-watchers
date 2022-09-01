from typing import Dict, Text

from watchers import base_watcher
from watchers.checkfront import base_checkfront


class GMCHuts(base_checkfront.BaseCheckfront):

  @property
  def url_template(self) -> Text:
    return "https://greenmountainclub.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id=2&filter_category_id=2&filter_item_id={filter_item_id}"

  @property
  def site_id_to_num_id(self) -> Dict[base_watcher.SiteId, int]:
    return {
        "wheeler_pond_camps": 3,
        "bryant_camp": 9,
        "bolton_lodge": 11,
    }
