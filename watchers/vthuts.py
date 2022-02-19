from typing import Dict, Text

from .checkfront import CheckFrontWatcher


class VTHutsWatcher(CheckFrontWatcher):

  @property
  def name(self) -> Text:
    return "VTHuts"

  @property
  def base_url(self) -> Text:
    return "https://vermonthuts.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id={category_id}&filter_category_id={filter_category_id}&filter_item_id={filter_item_id}"

  @property
  def cabins(self) -> Dict[int, Text]:
    return {
        42: "Dark Star Cabin",
        41: "Spikehorn Yurt",
        40: "Butternut Cabin",
        6: "Crow's Nest Yurt",
        4: "Triple Creek Cabin",
        2: "Nulhegan Hut",
        1: "Chittenden Brooke Hut",
    }
