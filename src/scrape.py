from __future__ import annotations

import sys
from pathlib import Path

import requests

DEFAULT_URL = (
    "https://www.wpanetwork.com/widgets/widget-team-schedule.php"
    "?school_year=2026-27&school_id=61&sport_id=11&level_id=10&output_mode=plain"
)
JV_URL = (
    "https://www.wpanetwork.com/widgets/widget-team-schedule.php"
    "?school_year=2026-27&school_id=61&sport_id=11&level_id=11&output_mode=plain"
)


def fetch_schedule_html(url: str = DEFAULT_URL, timeout: int = 30) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def save_schedule(url: str, filename: str) -> None:
    output_dir = Path(__file__).resolve().parents[1] / "output"
    output_dir.mkdir(exist_ok=True)

    html = fetch_schedule_html(url)
    output_path = output_dir / filename
    output_path.write_text(html, encoding="utf-8")
    print(f"Saved schedule HTML to {output_path}")


def main() -> int:
    save_schedule(DEFAULT_URL, "raw_schedule.html")
    save_schedule(JV_URL, "raw_jv_schedule.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
