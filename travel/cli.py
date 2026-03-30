import webbrowser
from pathlib import Path

import click

from . import parser, renderer

OUTPUT_DIR = Path("output")
TRIPS_DIR = Path("trips")


@click.group()
def cli():
    """Travel agenda — visualize your trip program."""


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
@click.option("--no-open", is_flag=True, default=False, help="Don't open browser automatically.")
def render(yaml_file: Path, no_open: bool):
    """Render a trip YAML to a static HTML file."""
    try:
        trip = parser.load(str(yaml_file))
    except Exception as e:
        raise click.ClickException(f"Could not parse {yaml_file}: {e}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{yaml_file.stem}.html"

    renderer.render(trip, output_path, yaml_path=yaml_file)
    click.echo(f"✓ Rendered: {output_path}")

    if not no_open:
        webbrowser.open(output_path.resolve().as_uri())


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
@click.option("--port", default=5173, show_default=True, help="Local port to listen on.")
def serve(yaml_file: Path, port: int):
    """Serve the trip agenda locally with live editing."""
    from . import server
    server.serve(yaml_file, port)


@cli.command("render-all")
def render_all():
    """Render all trips in the trips/ directory and generate an index page."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not TRIPS_DIR.exists():
        raise click.ClickException("No trips/ directory found.")

    yaml_files = sorted(TRIPS_DIR.glob("*.yaml"))
    if not yaml_files:
        raise click.ClickException("No YAML files found in trips/.")

    trips = []
    for yaml_file in yaml_files:
        try:
            trip = parser.load(str(yaml_file))
        except Exception as e:
            click.echo(f"  ✗ Skipped {yaml_file.name}: {e}", err=True)
            continue
        output_path = OUTPUT_DIR / f"{yaml_file.stem}.html"
        renderer.render(trip, output_path, yaml_path=yaml_file)
        trips.append((yaml_file.stem, trip))
        click.echo(f"  ✓ {yaml_file.name} → {output_path}")

    renderer.render_index(trips, OUTPUT_DIR / "index.html")
    click.echo(f"  ✓ index.html ({len(trips)} trips)")


@cli.command()
@click.argument("name")
def new(name: str):
    """Create a new trip YAML file from a template."""
    TRIPS_DIR.mkdir(exist_ok=True)
    slug = name.lower().replace(" ", "-")
    path = TRIPS_DIR / f"{slug}.yaml"

    if path.exists():
        raise click.ClickException(f"File already exists: {path}")

    path.write_text(_trip_template(name), encoding="utf-8")
    click.echo(f"✓ Created: {path}")
    click.echo(f"  Edit the file and run: travel serve {path}")


@cli.command()
@click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
def validate(yaml_file: Path):
    """Validate a trip YAML file structure."""
    try:
        trip = parser.load(str(yaml_file))
    except Exception as e:
        raise click.ClickException(f"Invalid file: {e}")

    total = sum(len(day.activities) for city in trip.cities for day in city.days)
    click.echo(f"✓ Valid — {len(trip.cities)} cities, {total} activities")


def _trip_template(name: str) -> str:
    from datetime import date, timedelta

    today = date.today()
    tomorrow = today + timedelta(days=1)

    return f"""\
title: {name}

cities:
  - name: City Name
    country: Country
    arrival: {today.isoformat()}
    departure: {tomorrow.isoformat()}
    notes: Optional notes about the city (can be removed)
    days:
      - date: {today.isoformat()}
        activities:
          - name: Activity Name
            time: "10:00"
            # Categories: food, nature, culture, entertainment, shopping, transport, sport, general
            category: culture
            notes: Optional description (can be removed)
            # booking: required  # uncomment if booking is needed
"""
