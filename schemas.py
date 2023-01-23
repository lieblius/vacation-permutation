from dataclasses import field
from typing import List

from marshmallow_dataclass import dataclass

from config import API_KEY


@dataclass
class FixedDate:
    year: int = field(default=0)
    month: int = field(default=0)
    day: int = field(default=0)


@dataclass
class QueryPlace:
    iata: str = field(default='')


@dataclass
class OriginPlace:
    queryPlace: QueryPlace


@dataclass
class DestinationPlace:
    queryPlace: QueryPlace


@dataclass
class QueryLeg:
    originPlace: OriginPlace
    destinationPlace: DestinationPlace
    fixedDate: FixedDate


@dataclass
class Query:
    queryLegs: List[QueryLeg]
    market: str = field(default='US')
    locale: str = field(default='en-US')
    currency: str = field(default='USD')


@dataclass
class RequestBody:
    query: Query


@dataclass
class Headers:
    content_type: str = field(default="application/json", metadata={"data_key": "Content-Type"})
    x_api_key: str = field(default=API_KEY, metadata={"data_key": "x-api-key"})


def request_body_factory(from_="", to="", year=0, month=0, day=0):
    query_leg = QueryLeg(originPlace=OriginPlace(QueryPlace(from_)), destinationPlace=DestinationPlace(QueryPlace(to)),
                         fixedDate=FixedDate(year=year, month=month, day=day))
    query = Query(queryLegs=[query_leg])
    return RequestBody(query)


def headers_factory():
    return Headers()
