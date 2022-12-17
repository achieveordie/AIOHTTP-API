# -*- coding: utf-8 -*-
"""Basic Pydantic Models to get reference of Tables."""
from typing import Union
from datetime import date
from pydantic import BaseModel


class PortSchema(BaseModel):
    code: str
    name: str
    parent_slug: str


class RegionSchema(BaseModel):
    slug: str
    name: str
    parent_slug: Union[str, None]


class PriceSchema(BaseModel):
    orig_code: str
    dest_code: str
    day: date
    price: int
