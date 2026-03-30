# travel-agenda

A small tool to visualize family trip programs — built entirely through conversation with Claude Code, without writing a single line of code by hand.

**Live site: [deveaud-m.github.io/travel-agenda](https://deveaud-m.github.io/travel-agenda/)**

---

## How it works

Trips are stored as simple YAML files in `trips/`. The tool renders them as a visual timeline (left to right, by day) with morning / afternoon / evening slots, Google Maps links, and booking status badges.

Pushing to `main` automatically deploys to GitHub Pages via GitHub Actions.

## Usage

```bash
# Install
uv sync

# Serve a trip locally with live reload
uv run travel serve trips/berlin-2026.yaml

# Render all trips to output/ (what CI runs)
uv run travel render-all

# Create a new trip from a template
uv run travel new "Tokyo 2027"
```

## Editing trips

Click the **Edit agenda** button on any trip page to open the YAML file directly in GitHub's web editor. Save and commit — the site redeploys in about a minute.
