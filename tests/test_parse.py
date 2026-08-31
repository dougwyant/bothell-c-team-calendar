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
          <table>
            <tr><td>9/10/2026</td><td>7:00 PM</td><td>Bothell vs Issaquah</td><td>Bothell HS</td></tr>
            <tr><td>9/12/2026</td><td>6:30 PM</td><td>Shorecrest vs Eastlake</td><td>Shorecrest Field</td></tr>
          </table>
        </body></html>
        """

        games = extract_games(html)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["away_team"], "Bothell")
        self.assertEqual(games[0]["home_team"], "Issaquah")
        self.assertEqual(games[0]["location"], "Bothell HS")

    def test_parse_game_datetime_handles_common_formats(self):
        value = parse_game_datetime("9/10/2026", "7:00 PM")
        self.assertIsNotNone(value)
        self.assertEqual(value.strftime("%Y-%m-%d %H:%M"), "2026-09-10 19:00")


if __name__ == "__main__":
    unittest.main()
