# -*- coding: utf-8 -*-
"""Validate result from DB and format it apt. before sending."""
from datetime import timedelta, date


# borrowed from https://stackoverflow.com/a/1060330/13170092
def _daterange(start_date, end_date):
    """ """
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def validate(data, date_from, date_to):
    """
    Validates result to conforms to the expected format
    :param data:
    :param date_to:
    :param date_from:
    :return:
    """
    iso_date_from = date.fromisoformat(date_from)
    iso_date_to = date.fromisoformat(date_to)

    data_price_dict = {}
    for single_data in data:
        if single_data["days"] > 2:
            data_price_dict[single_data["day"]] = round(single_data["average_price"])

    return [
        {
            "day": curr_date.strftime("%Y-%m-%d"),
            "average_price": data_price_dict.get(curr_date)
        }
        for curr_date in _daterange(iso_date_from, iso_date_to)
    ]
