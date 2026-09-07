# Bothell HS Soccer Calendar Feeds

[![Deploy status](https://github.com/dougwyant/bothell-c-team-calendar/actions/workflows/update-calendar.yml/badge.svg)](https://github.com/dougwyant/bothell-c-team-calendar/actions/workflows/update-calendar.yml)

This project generates Google Calendar-compatible ICS feeds for Bothell High School C-Team and JV soccer games from the KingCo athletics schedule. Event titles are prefixed with `BHS JVC` and `BHS JV`, respectively.

## Goals

- Download the schedule widget HTML
- Parse all games
- Keep only Bothell games
- Generate stable, subscribe-able `bothell-c-team.ics` and `bothell-jv-team.ics` files
- Refresh automatically with a GitHub Action
- Publish the output via GitHub Pages

## Local setup

```bash
python -m pip install -r requirements.txt
python src/scrape.py
python src/build_ics.py --input output/raw_schedule.html --output output/bothell-c-team.ics
python src/build_ics.py --input output/raw_jv_schedule.html --output output/bothell-jv-team.ics --calendar-id bothell-jv-team
```

## GitHub Pages setup

1. Create a GitHub repo for this project.
2. Enable GitHub Pages in the repo settings.
3. Choose the `Actions` deployment source if prompted.
4. Use the included workflow to publish the generated ICS file.

## Google Calendar subscription

1. In Google Calendar, click the "+" next to "Other calendars".
2. Select "From URL".
3. Paste the published ICS URL, for example:

```text
https://dougwyant.github.io/bothell-c-team-calendar/bothell-c-team-v3.ics
```

For the JV team, use:

```text
https://dougwyant.github.io/bothell-c-team-calendar/bothell-jv-team-v3.ics
```

4. Click "Add calendar".

## Notes

- This version intentionally uses a robust parser and stable UIDs so Google Calendar can refresh updates cleanly.
- If the source site exposes a JSON endpoint later, replace the scraper with that API for greater reliability.
