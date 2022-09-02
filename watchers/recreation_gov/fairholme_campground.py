from typing import Dict, Text

from watchers.base_watcher import SiteId
from watchers.recreation_gov.base_recreation_gov import BaseRecreationGov


class FairholmeCampground(BaseRecreationGov):

  @property
  def rec_id_to_site_id(self) -> Dict[Text, SiteId]:
    # This list is very incomplete, but it demonstrates how it works at least.
    return {"10169499": "1", "10169500": "2"}

  @property
  def campground_id(self) -> Text:
    return "259084"
