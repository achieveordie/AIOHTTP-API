# -*- coding: utf-8 -*-
"""Tests related to main functionality of the app."""
from starlette.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_single_port(monkeypatch):
    """Monkeypatch db-fetching(give mock data) to see if app works for Ports"""
    result = {
        "code": "CNCWN",
        "name": "Chiwan",
        "parent_slug": "china_south_main"
    }

    def _mock_get_port():
        return result

    monkeypatch.setattr(main, "_get_port", _mock_get_port)

    response = client.get("/rates/get_single_port")
    assert response.status_code == 200
    assert response.json() == result


def test_single_region(monkeypatch):
    """Monkeypatch db-fetching(give mock data) to see if app works for Regions"""
    result = {
        "slug": "china_main",
        "name": "China Main",
        "parent_slug": None
    }

    def _mock_get_region():
        return result

    monkeypatch.setattr(main, "_get_region", _mock_get_region)

    response = client.get("/rates/get_single_region")
    assert response.status_code == 200
    assert response.json() == result


def test_single_price(monkeypatch):
    """Monkeypatch db-fetching(give mock data) to see if app works for Prices"""
    result = {
        "orig_code": "CNGGZ",
        "dest_code": "EETLL",
        "day": "2016-01-01",
        "price": 1244
    }

    def _mock_get_price():
        return result

    monkeypatch.setattr(main, "_get_price", _mock_get_price)

    response = client.get("/rates/get_single_price")
    assert response.status_code == 200
    assert response.json() == result
