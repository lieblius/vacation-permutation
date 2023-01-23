from datetime import datetime


def parse_date(date: str):
    if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
        raise ValueError("Invalid date. The date must be in the future")

    date_list = date.split("-")
    year = int(date_list[0])
    month = int(date_list[1])
    day = int(date_list[2])
    return year, month, day
