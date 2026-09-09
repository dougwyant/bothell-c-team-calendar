from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parse import extract_games, parse_game_datetime


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "event"


def build_ics(
    events: Iterable[dict],
    calendar_id: str = "bothell-c-team",
    event_prefix: str = "",
) -> str:
    calendar = Calendar()
    calendar.add("prodid", f"-//Bothell {calendar_id.removeprefix('bothell-').replace('-', ' ').title()} Calendar//EN")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    calendar.add("x-wr-calname", calendar_id.replace("-", " ").title())
    local_timezone = ZoneInfo("America/Los_Angeles")

    for index, event in enumerate(events):
        local_start = parse_game_datetime(event.get("date", ""), event.get("time", ""))
        if local_start is None:
            continue

        start = local_start.replace(tzinfo=local_timezone).astimezone(timezone.utc)
        matchup = f"{event.get('away_team', 'Bothell')} @ {event.get('home_team', 'Opponent')}"
        summary = f"{event_prefix} {matchup}".strip()
        away = slugify(event.get("away_team", "bothell"))
        home = slugify(event.get("home_team", "opponent"))
        location = slugify(event.get("location", "bothell-hs"))
        uid = f"{local_start:%Y%m%d}-{away}-{home}-{location}@{calendar_id}-calendar-v4"
        end = start + timedelta(hours=2)

        cal_event = Event()
        cal_event.add("uid", uid)
        cal_event.add("dtstamp", datetime.now(timezone.utc))
        cal_event.add("dtstart", start)
        cal_event.add("dtend", end)
        cal_event.add("summary", summary)
        cal_event.add("location", event.get("location", "Bothell HS"))
        calendar.add_component(cal_event)

    return calendar.to_ical().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an ICS file from Bothell schedule rows.")
    parser.add_argument("--input", default="output/raw_schedule.html", help="HTML file with schedule rows")
    parser.add_argument("--output", default="output/bothell-c-team.ics", help="Generated ICS file")
    parser.add_argument("--calendar-id", default="bothell-c-team", help="Stable calendar identifier for UIDs")
    parser.add_argument("--event-prefix", default="", help="Prefix added to each event summary")
    args = parser.parse_args()

    raw_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        raise FileNotFoundError(f"Input HTML not found: {raw_path}")

    html = raw_path.read_text(encoding="utf-8")
    games = extract_games(html)
    filtered = [game for game in games if "bothell" in " | ".join([game.get("away_team", ""), game.get("home_team", "")]).lower()]
    output_path.write_text(
        build_ics(filtered, args.calendar_id, args.event_prefix),
        encoding="utf-8",
    )
    print(f"Wrote {len(filtered)} Bothell events to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
