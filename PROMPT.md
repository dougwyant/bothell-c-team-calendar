# Bothell HS C-Team Calendar Feed

Goal:
Create a system that generates a Google Calendar subscribable ICS feed for the Bothell High School C-Team schedule from KingCo Athletics.

Source:
https://www.wpanetwork.com/widgets/widget-league-sport-tabs.php?sport_id=11&league_id=7&school_year=2026-27&level_id=10&output_mode=plain

Requirements:
- Download the HTML page.
- Parse all schedule entries.
- Filter only games involving Bothell.
- Generate `bothell-c-team.ics`.
- Use stable UID values for events.
- Preserve updates when game times or locations change.
- Run automatically via GitHub Actions daily.
- Publish the ICS file via GitHub Pages.
- Include README with Google Calendar subscription instructions.
- Python implementation preferred.
- Use `requests`, `beautifulsoup4`, and `icalendar` libraries.
- Create unit tests for parsing logic.
