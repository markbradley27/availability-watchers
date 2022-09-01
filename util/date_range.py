import datetime


class DateRange():
  """Represents a range of dates, where the begin and end bounds are
  inclusive."""

  def __init__(self, begin: datetime.date, end: datetime.date):
    if (end < begin):
      raise ValueError("end date must be greater than or equal to begin date")
    self._begin = begin
    self._end = end

  @property
  def begin(self) -> datetime.date:
    return self._begin

  @property
  def end(self) -> datetime.date:
    return self._end

  def __str__(self):
    return "[{} - {}]".format(
        self._begin.strftime("%Y-%m-%d"), self._end.strftime("%Y-%m-%d"))

  # Bit of a hack perhaps, but just returns a copy of itself. DateRange itself
  # is an iterator.
  def __iter__(self):
    return DateRange(self._begin, self._end)

  def __next__(self):
    if (self._begin > self._end):
      raise StopIteration
    ret = self._begin
    self._begin += datetime.timedelta(1)
    return ret
