import json
from dataclasses import dataclass
from datetime import datetime
from typing import List

from aalto_news_gen.serializers.datetime_serializer import DateTimeEncoder


@dataclass
class Article:
    uuid: str
    lead: str
    article: str
    domain: str
    url: str
    date_of_creation: datetime
    cc_date: datetime

    def to_json(self) -> str:
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
