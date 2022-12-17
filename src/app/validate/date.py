# -*- coding: utf-8 -*-
"""Validates that provided date range is valid before sending them to DB."""
import re
from datetime import date


def validate(date_from, date_to):
    """
    Validates whether :
        1. provided date range is in correct format or not(YYYY-MM-DD)
        2. `date_from` occurs before `date_to`
    :param date_from: str
        starting date, Eg: "2016-01-01"
    :param date_to: str
        ending date, Eg: "2016-01-10"
    :return: str
        either of "f_format_wrong"/"f_order_wrong"/"success"
    """

    pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    for g_date in [date_from, date_to]:
        if pattern.match(g_date) is None:
            return "f_format_wrong"

    iso_from = date.fromisoformat(date_from)
    iso_to = date.fromisoformat(date_to)

    if int((iso_from - iso_to).days) > 0:
        return "f_order_wrong"

    return "success"
