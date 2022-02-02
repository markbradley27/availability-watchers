from .checkfront import CheckFrontWatcher


class GMCWatcher(CheckFrontWatcher):

  NAME = "GMCHuts"

  _BASE_URL = "https://greenmountainclub.checkfront.com/reserve/api/?call=calendar_days&start_date={start_date}&end_date={end_date}&category_id=2&filter_category_id=2&filter_item_id={filter_item_id}"

  _CABINS = {
      3: "Wheeler Pond Camps",
      9: "Bryant Camp",
      11: "Bolton Lodge",
  }
