from __future__ import annotations

import argparse
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Iterable

from icalendar import Calendar, Event

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parse import extract_games, parse_game_datetime


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "event"


def build_ics(events: Iterable[dict]) -> str:
    calendar = Calendar()
    calendar.add("prodid", "-//Bothell C-Team Calendar//EN")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")

    for index, event in enumerate(events):
        start = parse_game_datetime(event.get("date", ""), event.get("time", ""))
        if start is None:
            continue

        summary = f"{event.get('away_team', 'Bothell')} @ {event.get('home_team', 'Opponent')}"
        uid = f"{start.strftime('%Y%m%d')}-{slugify(event.get('away_team', 'bothell'))}-{slugify(event.get('home_team', 'opponent'))}"
        end = start + timedelta(hours=2)

        cal_event = Event()
        cal_event.add("uid", uid)
        cal_event.add("dtstamp", start)
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
    args = parser.parse_args()

    raw_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        raise FileNotFoundError(f"Input HTML not found: {raw_path}")

    html = raw_path.read_text(encoding="utf-8")
    games = extract_games(html)
    filtered = [game for game in games if "bothell" in " | ".join([game.get("away_team", ""), game.get("home_team", "")]).lower()]
    output_path.write_text(build_ics(filtered), encoding="utf-8")
    print(f"Wrote {len(filtered)} Bothell events to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
