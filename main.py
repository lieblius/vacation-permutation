import logging
import re
from datetime import datetime, timedelta
from itertools import permutations
from math import inf, factorial

import requests
from marshmallow_dataclass import class_schema

from config import URL
from schemas import request_body_factory, RequestBody, headers_factory, Headers
from utils import parse_date


class Flight:
    _headers = {}
    _payload = ""
    _year = 0
    _month = 0
    _day = 0

    def __init__(self, from_, to, date):
        iata_code_pattern = re.compile("^[A-Z]{3}$")
        if not iata_code_pattern.match(from_):
            raise ValueError("Invalid IATA code for departure location")
        if not iata_code_pattern.match(to):
            raise ValueError("Invalid IATA code for arrival location")
        if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
            raise ValueError("Invalid date. The date must be in the future")
        self.from_ = from_
        self.to = to
        self.date = date

        self._year, self._month, self._day = parse_date(self.date)

        self._resolve_headers()
        self._resolve_request_payload()

    def _resolve_request_payload(self):
        request_body = request_body_factory(from_=self.from_, to=self.to, year=self._year, month=self._month,
                                            day=self._day)
        request_body_schema = class_schema(RequestBody)()
        self._payload = request_body_schema.dumps(request_body)

    def _resolve_headers(self):
        headers = headers_factory()
        headers_schema = class_schema(Headers)()
        self._headers = headers_schema.dump(headers)

    def get_price(self):
        price = inf
        response = requests.post(URL, data=self._payload, headers=self._headers)
        assert response.status_code == 200, f"Request failed, status code {response.status_code}"

        try:
            if len(response.json()['content']['results']['quotes']) == 0:
                raise Exception("No flights found")
            price = int(list(response.json()['content']['results']['quotes'].values())[0]['minPrice']['amount'])
        except Exception as e:
            logging.exception(e)

        return price


def minimize_trip_price(data, home=None, start_date=datetime.today().strftime("%Y-%m-%d")):
    start_date = datetime(*parse_date(start_date))
    flight_permutations = permutations(data)
    assert factorial(len(data)) <= 120

    min_price = inf
    price_cache = {}
    optimal_order = []
    optimal_order_prices = []
    optimal_order_dates = []

    for flight_order in flight_permutations:
        date = start_date
        total_price = 0
        if home:
            flight_order = ((home, 0),) + flight_order + ((home, 0),)
        flight_order_prices = []
        flight_order_dates = []

        for i in range(len(flight_order) - 1):
            flight = Flight(flight_order[i][0], flight_order[i + 1][0], date.strftime("%Y-%m-%d"))

            flight_key = (flight.from_, flight.to, flight.date)

            if flight_key in price_cache:
                price = price_cache[flight_key]
            else:
                price = flight.get_price()
                price_cache[flight_key] = price

            total_price += price
            flight_order_prices.append(price)
            flight_order_dates.append(date.strftime("%Y-%m-%d"))

            date += timedelta(days=flight_order[i + 1][1])

        logging.info(f"\nTotal price: {total_price}\nOrder: {flight_order}\nPrices: "
                     f"{flight_order_prices}\nDates: {flight_order_dates}\n")

        if total_price < min_price:
            min_price = total_price
            optimal_order = flight_order
            optimal_order_prices = flight_order_prices
            optimal_order_dates = flight_order_dates

    return min_price, optimal_order, optimal_order_prices, optimal_order_dates


def main():
    logging.getLogger().setLevel(logging.INFO)

    data = [("LHR", 5), ("BER", 3), ("CDG", 4), ("FCO", 3)]
    min_price, optimal_order, optimal_order_prices, optimal_order_dates = minimize_trip_price(data=data, home="MIA",
                                                                                              start_date="2023-06-08")
    print(f"\nMin price: {min_price}\nOptimal order: {optimal_order}\nOptimal order prices: "
          f"{optimal_order_prices}\nOptimal order dates: {optimal_order_dates}")


if __name__ == "__main__":
    main()
