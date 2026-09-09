import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.parse import extract_games, parse_game_datetime


class ParseTestCase(unittest.TestCase):
    def test_extract_games_keeps_bothell_matches(self):
        html = """
        <html><body>
          <div class="schedule_contents">
            <div class="schedule_date_heading">Tuesday, Sep 1</div>
            <div class="schedule_date_contents">
              <div class="event_container">7:00 pm | Issaquah | Bothell | Conference | Bothell HS</div>
              <div class="event_container">6:30 pm | Shorecrest | Eastlake | Eastlake HS</div>
            </div>
          </div>
        </body></html>
        """

        games = extract_games(html)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["away_team"], "Issaquah")
        self.assertEqual(games[0]["home_team"], "Bothell")
        self.assertEqual(games[0]["location"], "Bothell HS")

    def test_parse_game_datetime_handles_common_formats(self):
        value = parse_game_datetime("Tuesday, Sep 1", "7:00 pm")
        self.assertIsNotNone(value)
        self.assertEqual(value.strftime("%Y-%m-%d %H:%M"), "2026-09-01 19:00")

    def test_extract_games_handles_team_schedule_table(self):
        html = """
        <table class="team_schedule"><tbody>
          <tr>
            <td><div class="event_date">Wed Sep 16</div><div class="event_time">6:30 pm</div></td>
            <td><div class="event_opponent">Skyline</div></td>
            <td><div class="event_ha">Home</div><div class="event_location">Bothell HS</div></td>
          </tr>
        </tbody></table>
        """
        games = extract_games(html)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["home_team"], "Bothell")
        self.assertEqual(games[0]["away_team"], "Skyline")
        self.assertEqual(parse_game_datetime(games[0]["date"], games[0]["time"]).strftime("%Y-%m-%d"), "2026-09-16")


if __name__ == "__main__":
    unittest.main()
