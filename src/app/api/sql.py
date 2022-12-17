# -*- coding: utf-8 -*-
"""Execute different SQL queries as per condition."""
"""
Please note that queries are not broken down into smaller strings
to promote readability over a smaller file. This may result in few extra lines.
"""


async def _execute_get_slug_from_parent(
        conn,
        parent_slug
):
    """
    Helper function that is called to get regions that has this `parent_slug`.
    :param conn: asyncpg.Connection Object
    :param parent_slug: str
    :return: List[str]
        result of the query in form of a list.
    """
    data = await conn.fetch(
        f"""
        SELECT slug
            FROM Regions
            WHERE parent_slug='{parent_slug}'
        """
    )

    # if above query fetches more than zero results then given region was main
    if len(data) > 0:
        data = [i['slug'] for i in data]
    # else given region was a sub-region
    else:
        data = []

    # also add the main region(if present) in list of sub-regions to search
    # since some port are directly associated to the main region than sub-regions
    data.append(parent_slug)
    return '\', \''.join([d for d in data])


async def execute_when_both_ports(
        conn,
        origin,
        destination,
        date_from,
        date_to,
):
    """
    The function that is called when `origin` and `destination` are determined to be ports by validators.
    The simplest form of query since it only requires one query to get required data.
    :param conn: asyncpg.Connection object
    :param origin: str
    :param destination: str
    :param date_from: str in format "YYYY-MM-DD"
    :param date_to: str in format "YYYY-MM-DD"
    :return: List[asyncpg.Record]
    """

    return await conn.fetch(
        f"""
        SELECT COUNT(*) AS days, 
               AVG(price) AS average_price,
               day
            FROM Prices
            WHERE orig_code='{origin}' AND
                  dest_code='{destination}' AND
                  (day BETWEEN '{date_from}' AND '{date_to}')
            GROUP BY day;
        """
    )


async def execute_when_one_region(
        conn,
        origin,
        destination,
        date_from,
        date_to,
        first_is_region,
):
    """
    The function that is called when either `origin` or `destination` is region (but not both).
    A slightly more complicated querying is required since it not only requires two queries,
    but also sub-querying in the second query.
    :param conn: asyncpg.Connection object
    :param origin: str
    :param destination: str
    :param date_from: str in format "YYYY-MM-DD"
    :param date_to: str in format "YYYY-MM-DD"
    :param first_is_region: bool
        If True, then signifies that `origin` is determined to be region as per validators.
        Else, `destination` is region.
    :return: List[asyncpg.Record]
    """
    region = origin if first_is_region else destination

    data = await _execute_get_slug_from_parent(conn, region)

    # if `origin` contains region then subquery for orig_code
    if first_is_region:
        data = await conn.fetch(
            f"""
            SELECT COUNT(*) AS days,
                   AVG(price) AS average_price,
                   day
                FROM Prices
                WHERE
                    orig_code IN 
                        (SELECT code
                            FROM Ports
                            WHERE parent_slug IN ('{data}')) AND
                    dest_code='{destination}' AND
                    (day BETWEEN '{date_from}' AND '{date_to}')
                GROUP BY day
                ORDER BY day
            """
        )
    # else, dest_code should contain the subquery
    else:
        data = await conn.fetch(
            f"""
                    SELECT COUNT(*) AS days,
                           AVG(price) AS average_price,
                           day
                        FROM Prices
                        WHERE
                            orig_code='{origin}'AND
                            dest_code IN 
                                (SELECT code
                                    FROM Ports
                                    WHERE parent_slug IN ('{data}')) AND
                            (day BETWEEN '{date_from}' AND '{date_to}')
                        GROUP BY day
                        ORDER BY day
            """
        )
    return data


async def execute_when_both_region(
        conn,
        origin,
        destination,
        date_from,
        date_to,
):
    """
    Function that is called when both `origin` and `destination` are determined to be regions
    by the validators.
    Although it requires more querying, it is similar to above function in how it is written and smaller
    by virtue of it being non-conditional (both origin and destination are region so requires no condition).
    :param conn: asyncpg.Connection object
    :param origin: str
    :param destination: str
    :param date_from: str in format "YYYY-MM-DD"
    :param date_to: str in format "YYYY-MM-DD"
    :return: List[asyncpg.Record]
    """
    data_origin = await _execute_get_slug_from_parent(conn, origin)
    data_dest = await _execute_get_slug_from_parent(conn, destination)

    return await conn.fetch(
        f"""
        SELECT COUNT(*) AS days,
               AVG(price) AS average_price,
               day
            FROM Prices
            WHERE
                orig_code IN
                    (SELECT code
                        FROM Ports
                        WHERE parent_slug IN ('{data_origin}')) AND
                dest_code IN
                    (SELECT code
                        FROM Ports
                        WHERE parent_slug IN ('{data_dest}')) AND
                (day BETWEEN '{date_from}' AND '{date_to}')
            GROUP BY day
            ORDER BY day
        """
    )
