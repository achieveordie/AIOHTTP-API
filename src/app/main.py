import os
import asyncpg
from fastapi import FastAPI

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
    conn = connect_dict["conn"]

    type_date = date.validate(date_from, date_to)

    # type_date is a string, other than "success"
    # is a failure.
    if type_date == "f_format_wrong":
        # To-DO: Return more readable BaseModel class
        return {"temporary failure": "wrong format"}
    if type_date == "f_order_wrong":
        # To-DO: Return more readable BaseModel class
        return {"temporary failure": "wrong order"}

    type_loc = location.validate(origin, destination)

    # type_loc will be a 2-length tuple, if it contains
    # "neither", it implies that location validation failed.
    if "neither" in type_loc:
        # To-DO: Return more readable BaseModel class
        return {"temporary failure": "from validation_location"}

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


# Only here in case one needs to do sanity-check about
# existence of the db.
@app.get("/rates/get_single_port/", response_model=PortSchema)
async def single_port():
    conn = connect_dict['conn']

    data = await conn.fetchrow(
        """SELECT * FROM Ports LIMIT 1"""
    )

    return dict(data)


@app.get("/rates/get_single_region/", response_model=RegionSchema)
async def single_region():
    conn = connect_dict['conn']

    data = await conn.fetchrow(
        """SELECT * FROM Regions LIMIT 1"""
    )

    return dict(data)


@app.get("/rates/get_single_price/", response_model=PriceSchema)
async def single_price():
    conn = connect_dict['conn']

    data = await conn.fetchrow(
        """SELECT * FROM Prices LIMIT 1"""
    )

    return dict(data)
