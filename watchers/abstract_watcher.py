import abc
import datetime
import json
from typing import Dict, Text, Union

AvailabilityMap = Dict[datetime.date, bool]


class AbstractWatcher(abc.ABC):
  NAME = "Abstract"

  _SAVED_DATE_FORMAT = "%Y-%m-%d"

  @classmethod
  def filename(cls, id: Union[Text, int] = None) -> Text:
    if id is None:
      return "availability_files/{}_availability.json".format(cls.NAME)
    else:
      return "availability_files/{}_{}_availability.json".format(cls.NAME, id)

  @classmethod
  def load_availability(cls, id: Union[Text, int] = None) -> AvailabilityMap:
    try:
      with open(cls.filename(id), "r") as openings_file:
        formatted = json.loads(openings_file.read())
        return {
            datetime.datetime.strptime(k, cls._SAVED_DATE_FORMAT).date(): v
            for k, v in formatted.items()
        }
    except FileNotFoundError:
      return {}

  @classmethod
  def save_availability(cls,
                        availability: AvailabilityMap,
                        id: Union[Text, int] = None):
    with open(cls.filename(id), "w") as openings_file:
      formatted = {
          k.strftime(cls._SAVED_DATE_FORMAT): v
          for k, v in availability.items()
      }
      openings_file.write(json.dumps(formatted, sort_keys=True, indent=2))

  @staticmethod
  def diff_availability(saved: AvailabilityMap,
                        fetched: AvailabilityMap) -> AvailabilityMap:
    diff = {}
    for date in fetched.keys():
      if date not in saved or saved[date] != fetched[date]:
        diff[date] = fetched[date]
    return diff

  # Returns a map of changes in availability.
  # ID maps to a map of dates that map to true if the date is newly available
  # and false if the date is newly unavailable.
  @abc.abstractmethod
  def get_diffs(self, start_date: datetime.date,
                end_date: datetime.date) -> Dict[Text, AvailabilityMap]:
    pass
