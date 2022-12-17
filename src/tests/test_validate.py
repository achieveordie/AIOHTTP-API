# -*- coding: utf-8 -*-
"""Tests that all validation functions perform as expectation, covering 100% coverage."""
import pytest

from app.validate import date, location, result


class TestDate:
    def test_success(self):
        """Should return 'success' for apt. inputs"""
        dates_from = [
            "2016-12-01",
            "2015-01-12"
        ]

        dates_to = [
            "2016-12-05",
            "2015-01-12"
        ]

        for date_from, date_to in zip(dates_from, dates_to):
            result_ = date.validate(date_from, date_to)
            assert result_ == "success"

    def test_format_wrong(self):
        """Should return 'f_format_wrong' for erroneous inputs"""
        dates_from = [
            "999-01-12",
            "01-01-12",
            "2012-01-01",
            "2020-10-10",
        ]

        dates_to = [
            "2012-01-01",
            "2020-10-10",
            "200-01-090",
            "01-01-1",
        ]

        for date_from, date_to in zip(dates_from, dates_to):
            result_ = date.validate(date_from, date_to)
            assert result_ == "f_format_wrong"

    def test_order_wrong(self):
        """Should return 'f_order_wrong' for when date_from > date_to"""
        dates_from = [
            "2020-01-02",
            "2015-08-24"
        ]

        dates_to = [
            "2020-01-01",
            "2015-07-24",
        ]

        for date_from, date_to in zip(dates_from, dates_to):
            result_ = date.validate(date_from, date_to)
            assert result_ == "f_order_wrong"


class TestLocation:
    # dict to check that all combination only touched once in `test_location()`
    type_encountered = {
        "origin_port_dest_region": 0,
        "origin_region_dest_port": 0,
        "origin_port_dest_port": 0,
        "origin_region_dest_region": 0,
    }

    @pytest.mark.parametrize("origin", ["FIMTY", "norway_south_west"])
    @pytest.mark.parametrize("destination", ["RULED", "baltic"])
    def test_location(self, origin, destination):
        """Should only have one permutation of 'port'/'region'."""
        result_ = location.validate(origin, destination)

        assert "neither" not in result_

        if result_ == ("port", "port"):
            self.type_encountered["origin_port_dest_port"] += 1
            assert self.type_encountered["origin_port_dest_port"] == 1

        elif result_ == ("port", "region"):
            self.type_encountered["origin_port_dest_region"] += 1
            assert self.type_encountered["origin_port_dest_region"] == 1

        elif result_ == ("region", "port"):
            self.type_encountered["origin_region_dest_port"] += 1
            assert self.type_encountered["origin_region_dest_port"] == 1

        elif result_ == ("region", "region"):
            self.type_encountered["origin_region_dest_region"] += 1
            assert self.type_encountered["origin_region_dest_region"] == 1
        else:
            raise AssertionError("`result_` was a different combination "
                                 f"than 'port'/'region': {result_}")

    def test_location_is_neither(self):
        """Should give 'result' for erroneous input"""
        origins = [
            "baltiC",
            ""
        ]

        dests = [
            "",
            "RULEDED",
        ]

        for origin, dest in zip(origins, dests):
            result_ = location.validate(origin, dest)

            assert result_ == ("neither", "neither")


class TestResult:
    from datetime import date

    def test_1_days_iteration(self):
        """Should only iterate over 1 day as per input."""
        counter = 0
        for _ in result._daterange(
            self.date.fromisoformat("2012-01-01"),
            self.date.fromisoformat("2012-01-01")
        ):
            counter += 1

        assert counter == 1

    def test_2_days_iteration(self):
        """Should only iterate over 2 days as per input."""
        counter = 0
        for _ in result._daterange(
            self.date.fromisoformat("2012-01-01"),
            self.date.fromisoformat("2012-01-02")
        ):
            counter += 1

        assert counter == 2

    def test_5_days_iteration(self):
        """Should only iterate over 5 days as per input."""
        counter = 0
        for _ in result._daterange(
            self.date.fromisoformat("2012-01-01"),
            self.date.fromisoformat("2012-01-05")
        ):
            counter += 1

        assert counter == 5

    def test_10_days_iteration(self):
        """Should only iterate over 10 days as per input."""
        counter = 0
        for _ in result._daterange(
            self.date.fromisoformat("2012-01-01"),
            self.date.fromisoformat("2012-01-10")
        ):
            counter += 1

        assert counter == 10
