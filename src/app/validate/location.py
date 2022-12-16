# -*- coding: utf-8 -*-
"""Validates that provided locations are valid before sending them to DB."""


def validate(origin, destination):
    """
    Validates location based on:
    1. If either parameter belong to a port code
        checks if there are 5 character and all in uppercase
    2. If either parameter belong to a region slug
        Tries to find _(underscore) or if given parameter is all lowercase
    :param origin: str
    :param destination: str
    :return: tuple[str] of length 2
        where either element is either "region"/"port"/"neither"
    """
    def _check_port(string):
        """Helper private function to check if string belongs to port"""
        return len(string) == 5 and string.isupper()

    def _check_slug(string):
        """Helper private function to check if string belongs to slug"""
        return ("_" in string or string.islower()) and len(string) > 0

    origin = str(origin) if type(origin) != str else origin
    destination = str(destination) if type(destination) != str else destination

    loc_type = []
    for string in [origin, destination]:
        if _check_port(string):
            loc_type.append("port")
        elif _check_slug(string):
            loc_type.append("region")
        else:
            loc_type.append("neither")

    return tuple(loc_type)
