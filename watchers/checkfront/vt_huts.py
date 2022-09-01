from typing import Dict, Text

from watchers import base_watcher
from watchers.checkfront import base_checkfront


class VTHuts(base_checkfront.BaseCheckfront):

  @property
  def url_template(self) -> Text:
    return "https://vermonthuts.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id={category_id}&filter_category_id={filter_category_id}&filter_item_id={filter_item_id}"

  @property
  def site_id_to_num_id(self) -> Dict[base_watcher.SiteId, int]:
    return {
        "dark_star_cabin": 42,
        "spikehorn_yurt": 41,
        "butternut_cabin": 40,
        "crows_nest_yurt": 6,
        "triple_creek_cabin": 4,
        "nulhegan_hut": 2,
        "chittenden_brooke_hut": 1,
    }
