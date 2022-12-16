async def _execute_get_slug_from_parent(
        conn,
        parent_slug
):
    """

    :param conn:
    :param parent_slug:
    :return:
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

    :param conn:
    :param origin:
    :param destination:
    :param date_from:
    :param date_to:
    :return:
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

    :param conn:
    :param origin:
    :param destination:
    :param date_from:
    :param date_to:
    :param first_is_region:
    :return:
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

    :param conn:
    :param origin:
    :param destination:
    :param date_from:
    :param date_to:
    :return:
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
