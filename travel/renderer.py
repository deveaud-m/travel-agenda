from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from jinja2 import Environment, FileSystemLoader

from .parser import Trip

CITY_COLORS = [
    "#2563eb",
    "#16a34a",
    "#dc2626",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#be185d",
    "#854d0e",
]

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render(trip: Trip, output_path: Path, yaml_path: Optional[Path] = None, github_repo: Optional[str] = None) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    env.filters["date_fmt"] = _date_fmt
    env.filters["day_fmt"] = _day_fmt
    env.filters["short_day"] = _short_day
    env.filters["maplink"] = lambda a: f"https://www.google.com/maps/search/?api=1&query={quote_plus(a)}" if a else ""
    env.tests["in_slot"] = lambda activity, slot: slot in activity.slots

    city_colors = {
        city.name: CITY_COLORS[i % len(CITY_COLORS)]
        for i, city in enumerate(trip.cities)
    }

    yaml_content = yaml_path.read_text(encoding="utf-8") if yaml_path else ""
    yaml_filename = yaml_path.name if yaml_path else "trip.yaml"
    github_edit_url = (
        f"https://github.dev/{github_repo}/blob/main/trips/{yaml_filename}"
        if github_repo else None
    )

    template = env.get_template("agenda.html.j2")
    html = template.render(
        trip=trip,
        city_colors=city_colors,
        today=date.today(),
        yaml_content=yaml_content,
        yaml_filename=yaml_filename,
        github_edit_url=github_edit_url,
    )
    output_path.write_text(html, encoding="utf-8")


def render_index(trips: list, output_path: Path) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    env.filters["date_fmt"] = _date_fmt

    items = [
        {
            "trip": trip,
            "filename": f"{slug}.html",
            "color": CITY_COLORS[i % len(CITY_COLORS)],
            "slug": slug,
        }
        for i, (slug, trip) in enumerate(trips)
    ]
    template = env.get_template("index.html.j2")
    html = template.render(trips=items)
    output_path.write_text(html, encoding="utf-8")


def _date_fmt(d: date) -> str:
    return d.strftime("%B %-d, %Y") if d else ""


def _day_fmt(d: date) -> str:
    return d.strftime("%A %-d %B")


def _short_day(d: date) -> str:
    return d.strftime("%a %-d")
