from .checkfront import CheckFrontWatcher


class VTHutsWatcher(CheckFrontWatcher):

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
