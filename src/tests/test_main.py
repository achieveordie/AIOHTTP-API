import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_db_sanity_check(test_app):
    async with AsyncClient(app=test_app, base_url="http://localhost:8000/rates/") as ac:
        response_port = await ac.get("/get_single_port/")
        response_price = await ac.get("/get_single_price/")
        response_region = await ac.get("/get_single_region/")

    assert response_port.status_code == 200
    assert response_price.status_code == 200
    assert response_region.status_code == 200

    assert response_port.json() == {"code": "CNCWN",
                                    "name": "Chiwan",
                                    "parent_slug": "china_south_main"}

    assert response_region.json() == {"slug": "china_main",
                                      "name": "China Main",
                                      "parent_slug": None}

    assert response_price.json() == {"orig_code": "CNGGZ",
                                     "dest_code": "EETLL",
                                     "day": "2016-01-01",
                                     "price": 1244}

