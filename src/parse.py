from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List, Optional

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
    ]
    return any(re.match(pattern, text, re.IGNORECASE) for pattern in date_patterns)


def looks_like_time(value: str) -> bool:
    text = normalize_text(value)
    return bool(re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)?", text, re.IGNORECASE))


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
    for row in soup.find_all("tr"):
        game = parse_game_row(row)
        if game:
            entries.append(game)
    return entries


def parse_american_time(raw: str) -> Optional[datetime]:
    cleaned = normalize_text(raw)
    if not cleaned:
        return None
    for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_game_datetime(date_text: str, time_text: str) -> Optional[datetime]:
    parsed_date = None
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%b %d, %Y"):
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
