from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import yaml


CATEGORY_ICONS = {
    "food": "🍽️",
    "nature": "🌿",
    "culture": "🏛️",
    "entertainment": "🎭",
    "shopping": "🛍️",
    "transport": "🚌",
    "sport": "⚽",
    "general": "📍",
}


@dataclass
class Activity:
    name: str
    time: Optional[str] = None
    notes: Optional[str] = None
    booking: Optional[str] = None
    category: str = "general"
    address: Optional[str] = None

    @property
    def icon(self) -> str:
        return CATEGORY_ICONS.get(self.category, "📍")

    @property
    def slot(self) -> str:
        if self.time:
            try:
                hour = int(self.time.split(":")[0])
                if hour < 12:
                    return "morning"
                elif hour < 18:
                    return "afternoon"
                else:
                    return "evening"
            except (ValueError, IndexError):
                pass
        return "morning"


@dataclass
class Day:
    date: date
    activities: list[Activity] = field(default_factory=list)


@dataclass
class City:
    name: str
    arrival: date
    departure: date
    country: Optional[str] = None
    notes: Optional[str] = None
    accommodation: Optional[str] = None
    accommodation_address: Optional[str] = None
    days: list[Day] = field(default_factory=list)


@dataclass
class Trip:
    title: str
    cities: list[City]

    @property
    def start_date(self) -> date:
        return self.cities[0].arrival

    @property
    def end_date(self) -> date:
        return self.cities[-1].departure

    @property
    def duration(self) -> int:
        return (self.end_date - self.start_date).days


def load(path: str) -> Trip:
    with open(path) as f:
        data = yaml.safe_load(f)
    return _parse_trip(data)


def _parse_trip(data: dict) -> Trip:
    cities = [_parse_city(c) for c in data.get("cities", [])]
    return Trip(title=data["title"], cities=cities)


def _parse_city(data: dict) -> City:
    days = [_parse_day(d) for d in data.get("days", [])]
    return City(
        name=data["name"],
        arrival=data["arrival"],
        departure=data["departure"],
        country=data.get("country"),
        notes=data.get("notes"),
        accommodation=data.get("accommodation"),
        accommodation_address=data.get("accommodation_address"),
        days=sorted(days, key=lambda d: d.date),
    )


def _parse_day(data: dict) -> Day:
    activities = [_parse_activity(a) for a in data.get("activities", [])]
    return Day(date=data["date"], activities=activities)


def _parse_activity(data: dict) -> Activity:
    return Activity(
        name=data["name"],
        time=data.get("time"),
        notes=data.get("notes"),
        booking=data.get("booking"),
        category=data.get("category", "general"),
        address=data.get("address"),
    )
