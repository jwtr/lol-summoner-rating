import unittest
from unittest.mock import Mock

rate_summoner = __import__("rate_summoner")
score_match = rate_summoner.score_match
rate_summoner.config["summoner_name"] = "Josh"
rate_summoner.tier_multiplier = Mock(return_value=50)
rate_summoner.get_match_data = Mock(
    return_value={
        "gameDuration": 1619,
        "teams": [
            {
                "teamId": 100,
                "win": "Win",
                "towerKills": 7,
                "baronKills": 1,
                "dragonKills": 2,
                "riftHeraldKills": 2,
            },
        ],
        "participants": [
            {
                "participantId": 1,
                "teamId": 100,
                "stats": {
                    "kills": 9,
                    "deaths": 3,
                    "assists": 6,
                    "tripleKills": 0,
                    "quadraKills": 0,
                    "pentaKills": 0,
                    "totalDamageDealt": 152170,
                    "totalHeal": 7381,
                    "visionScore": 33,
                    "goldEarned": 14155,
                    "inhibitorKills": 1,
                    "totalMinionsKilled": 214,
                    "wardsPlaced": 12,
                    "wardsKilled": 9,
                    "firstBloodKill": False,
                    "firstBloodAssist": False,
                    "firstTowerKill": False,
                    "firstTowerAssist": True,
                    "firstInhibitorKill": False,
                    "firstInhibitorAssist": False,
                },
            },
        ],
        "participantIdentities": [
            {
                "participantId": 1,
                "player": {
                    "summonerName": "Josh",
                },
            },
        ],
    }
)


class TestRateSummoner(unittest.TestCase):
    def test_score_match(self):
        match_id = "1234567890"
        result = score_match(match_id)
        self.assertEqual(result, 56776)


if __name__ == "__main__":
    unittest.main()
