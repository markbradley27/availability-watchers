from typing import Dict, Text

from .checkfront import CheckFrontWatcher


class GMCWatcher(CheckFrontWatcher):

  @property
  def name(self) -> Text:
    return "GMCHuts"

  @property
  def base_url(self) -> Text:
    return "https://greenmountainclub.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id=2&filter_category_id=2&filter_item_id={filter_item_id}"

  @property
  def cabins(self) -> Dict[Text, int]:
    return {
        "wheeler_pond_camps": 3,
        "bryant_camp": 9,
        "bolton_lodge": 11,
    }
