# Bothell HS C-Team Calendar Feed

This project generates a Google Calendar-compatible ICS feed for Bothell High School C-Team games from the KingCo athletics schedule.

## Goals

- Download the schedule widget HTML
- Parse all games
- Keep only Bothell games
- Generate a stable, subscribe-able `bothell-c-team.ics` file
- Refresh automatically with a GitHub Action
- Publish the output via GitHub Pages

## Local setup

```bash
python -m pip install -r requirements.txt
python src/scrape.py
python src/build_ics.py --input output/raw_schedule.html --output output/bothell-c-team.ics
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
https://YOUR_USERNAME.github.io/bothell-c-team-calendar/bothell-c-team.ics
```

4. Click "Add calendar".

## Notes

- This version intentionally uses a robust parser and stable UIDs so Google Calendar can refresh updates cleanly.
- If the source site exposes a JSON endpoint later, replace the scraper with that API for greater reliability.
