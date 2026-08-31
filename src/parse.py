from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def looks_like_date(value: str) -> bool:
    text = normalize_text(value)
    if not text:
        return False
    date_patterns = [
        r"^\d{1,2}/\d{1,2}/\d{2,4}$",
        r"^\d{4}-\d{2}-\d{2}$",
        r"^[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}$",
        r"^\d{1,2}-\d{1,2}-\d{2,4}$",
        r"^[A-Za-z]+,\s*[A-Za-z]{3,9}\s+\d{1,2}$",
    ]
    return any(re.match(pattern, text, re.IGNORECASE) for pattern in date_patterns)


def looks_like_time(value: str) -> bool:
    text = normalize_text(value)
    return bool(re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)?", text, re.IGNORECASE))


def parse_date_heading(date_text: str, school_year: str = "2026-27") -> Optional[datetime]:
    cleaned = normalize_text(date_text)
    if not cleaned:
        return None

    start_year, end_year = [int(part) for part in school_year.split("-")]
    month_names = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

    for fmt in ("%A, %b %d", "%a, %b %d"):
        try:
            base = datetime.strptime(cleaned, fmt)
            year = start_year if base.month >= 8 else end_year
            return base.replace(year=year)
        except ValueError:
            continue

    for fmt in ("%b %d", "%B %d"):
        try:
            base = datetime.strptime(cleaned, fmt)
            year = start_year if base.month >= 8 else end_year
            return base.replace(year=year)
        except ValueError:
            continue

    return None


def parse_game_row(row) -> Optional[dict]:
    cells = [normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["td", "th"]) if normalize_text(cell.get_text(" ", strip=True))]
    if not cells:
        return None

    joined = " | ".join(cells)
    if "bothell" not in joined.lower():
        return None

    date_text = next((cell for cell in cells if looks_like_date(cell)), "")
    time_text = next((cell for cell in cells if looks_like_time(cell)), "")
    if not date_text:
        return None

    location = ""
    for cell in cells:
        if "bothell" in cell.lower() and any(token in cell.lower() for token in ["high", "school", "hs", "stadium", "field"]):
            location = cell
            break

    match = re.search(r"(?P<away>[^|@]+?)\s*(?:@|vs)\s*(?P<home>[^|]+)", joined, re.IGNORECASE)
    if match:
        away_team = normalize_text(match.group("away"))
        home_team = normalize_text(match.group("home"))
    else:
        away_team = ""
        home_team = ""
        for cell in cells:
            if "bothell" in cell.lower() and cell.lower() != "bothell":
                if away_team:
                    home_team = cell
                else:
                    away_team = cell
                break

    if not away_team and not home_team:
        return None

    if "bothell" in away_team.lower():
        home_team = home_team or (next((cell for cell in cells if "bothell" not in cell.lower() and cell.strip()), ""))
    elif "bothell" in home_team.lower():
        away_team = away_team or (next((cell for cell in cells if "bothell" not in cell.lower() and cell.strip()), ""))

    if not away_team or not home_team:
        return None

    return {
        "date": date_text,
        "time": time_text,
        "away_team": away_team,
        "home_team": home_team,
        "location": location or "Bothell HS",
    }


def extract_games(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    entries: List[dict] = []

    for date_block in soup.select(".schedule_date_contents"):
        heading = date_block.find_previous(class_="schedule_date_heading")
        date_text = normalize_text(heading.get_text(" ", strip=True)) if heading else ""
        if not date_text:
            continue

        for event in date_block.select(".event_container"):
            parts = [normalize_text(p) for p in event.get_text("|", strip=True).split("|") if normalize_text(p)]
            if len(parts) < 4:
                continue

            time_text = parts[0]
            away_team = parts[1]
            home_team = parts[2]
            location = parts[-1]

            if len(parts) >= 5 and "conference" in parts[3].lower():
                location = parts[-1]
            elif len(parts) >= 5 and "conference" not in parts[3].lower():
                location = parts[-1]

            if "bothell" not in away_team.lower() and "bothell" not in home_team.lower():
                continue

            entries.append({
                "date": date_text,
                "time": time_text,
                "away_team": away_team,
                "home_team": home_team,
                "location": location,
            })

    if entries:
        return entries

    for row in soup.find_all("tr"):
        game = parse_game_row(row)
        if game:
            entries.append(game)
    return entries


def parse_american_time(raw: str) -> Optional[datetime]:
    cleaned = normalize_text(raw)
    if not cleaned:
        return None

    cleaned = cleaned.lower().replace("am", " AM").replace("pm", " PM")
    for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p", "%I %p"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_game_datetime(date_text: str, time_text: str) -> Optional[datetime]:
    parsed_date = parse_date_heading(date_text)
    if parsed_date is None:
        for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
            try:
                parsed_date = datetime.strptime(normalize_text(date_text), fmt)
                break
            except ValueError:
                continue

    if parsed_date is None:
        return None

    parsed_time = parse_american_time(time_text)
    if parsed_time is None:
        return parsed_date.replace(hour=19, minute=0, second=0)

    return parsed_date.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0)
