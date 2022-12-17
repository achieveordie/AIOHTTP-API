# -*- coding: utf-8 -*-
"""Main file to encapsulate the functionality web app with the db."""
import os
import asyncpg
from fastapi import FastAPI, HTTPException

from .api.models import (
    PortSchema,
    RegionSchema,
    PriceSchema,
)
from .api.sql import (
    execute_when_one_region,
    execute_when_both_ports,
    execute_when_both_region,
)
from .validate import (
    date,
    location,
    result,
)


app = FastAPI()
connect_dict = {}


@app.on_event("startup")
async def startup():
    connect_dict['conn'] = await asyncpg.connect(os.getenv("DATABASE_URL"))


@app.on_event("shutdown")
async def shutdown():
    await connect_dict['conn'].close()


@app.get("/rates")
async def rates(
        date_from: str,
        date_to: str,
        origin: str,
        destination: str,
):
    """
    The initial and main entrypoint. It requires no path parameters and four query
    parameters as follows:
    :param date_from: str in format "YYYY-MM-DD"
        The date from which data is required to be queried.
    :param date_to: str in format "YYYY-MM-DD"
        The date till which (inclusive) data is required to be queried.
    :param origin: str
        The starting location, can either be a region(main/sub/middle) slug or a port code.
    :param destination: str
        The ending location, can either be a region(main/sub/middle) slug or a port code.
    :return: List[dict]
        The keys of each element will be:
            day: (str) representing the day for which average price is calculated.
            average_price: (int|None) representing average price of that day from `origin` to `destination`.
    """
    conn = connect_dict["conn"]

    type_date = date.validate(date_from, date_to)

    # type_date is a string, other than "success"
    # is a failure.
    if type_date == "f_format_wrong":
        raise HTTPException(status_code=418,
                            detail="Check Format of Provided Dates.")
    if type_date == "f_order_wrong":
        raise HTTPException(status_code=418,
                            detail="Date From > Date To.")

    type_loc = location.validate(origin, destination)

    # type_loc will be a 2-length tuple, if it contains
    # "neither", it implies that location validation failed.
    if "neither" in type_loc:
        raise HTTPException(status_code=503,
                            detail="Validation on location(s) are currently failing.")

    if type_loc[0] == type_loc[1] == "port":
        data = await execute_when_both_ports(
            conn,
            origin,
            destination,
            date_from,
            date_to
        )
    elif type_loc[0] == type_loc[1] == "region":
        data = await execute_when_both_region(
            conn,
            origin,
            destination,
            date_from,
            date_to,
        )
    else:
        first_is_region = True if type_loc[0] == "region" else False
        data = await execute_when_one_region(
            conn,
            origin,
            destination,
            date_from,
            date_to,
            first_is_region,
        )

    return result.validate(data, date_from, date_to)


# The following methods are only here in case one needs to
# do sanity-check about existence of the db and
# proper connection between db and app (for testing).
async def _get_port():
    """Helper private function to fetch one row from Ports table"""
    data = await connect_dict["conn"].fetchrow(
        """SELECT * FROM Ports LIMIT 1"""
    )
    return dict(data)


async def _get_price():
    """Helper private function to fetch one row from Ports table"""
    data = await connect_dict["conn"].fetchrow(
        """SELECT * FROM Prices LIMIT 1"""
    )
    return dict(data)


async def _get_region():
    """Helper private function to fetch one row from Regions table"""
    data = await connect_dict["conn"].fetchrow(
        """SELECT * FROM Regions LIMIT 1"""
    )
    return dict(data)


@app.get("/rates/get_single_port/", response_model=PortSchema)
async def single_port():
    return _get_port()


@app.get("/rates/get_single_region/", response_model=RegionSchema)
async def single_region():
    return _get_region()


@app.get("/rates/get_single_price/", response_model=PriceSchema)
async def single_price():
    return _get_price()
