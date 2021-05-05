"""Generates a LoL summoner rating
Ratings are based on recent solo queue performance
"""

import math
import sys
from riotwatcher import LolWatcher, ApiError

config = {
    "riot_api_key": "",
    "summoner_region": "",
    "summoner_name": "",
    "queue_id": 420,
    "fast_game_minutes": 25,
    "match_history_limit": 1,
}

lol_watcher = LolWatcher(config["riot_api_key"])


def rate_summoner() -> None:
    """Prints the summoner rating"""

    summoner = get_summoner(config["summoner_name"])
    match_list = get_match_list(summoner["accountId"])

    score = 0
    for match in match_list["matches"]:
        score += score_match(match["gameId"])

    print(
        '{summoner_name} has a "Josh Rating" of {score}'.format(
            summoner_name=config["summoner_name"], score=score
        )
    )


def get_summoner(summoner_name: str) -> dict:
    """Gets summoner data from the Riot API"""

    try:
        return lol_watcher.summoner.by_name(
            config["summoner_region"], summoner_name
        )
    except ApiError as err:
        if err.response.status_code == 404:
            report_error("Summoner could not be found.")
        else:
            raise


def get_match_list(summoner_account_id: str) -> dict:
    """Gets matchlist data from the Riot API"""

    try:
        return lol_watcher.match.matchlist_by_account(
            config["summoner_region"],
            summoner_account_id,
            config["queue_id"],
            None,
            None,
            None,
            config["match_history_limit"],
        )
    except ApiError as err:
        if err.response.status_code == 404:
            report_error("Match history could not be found.")
        else:
            raise


def get_match_data(match_id: int) -> dict:
    """Gets match data from the Riot API"""

    try:
        return lol_watcher.match.by_id(
            config["summoner_region"],
            match_id,
        )
    except ApiError as err:
        if err.response.status_code == 404:
            report_error("Match data could not be found.")
        else:
            raise


def get_league_data(summoner_id: str) -> dict:
    """Gets summoner league data from the Riot API"""

    try:
        league_data = lol_watcher.league.by_summoner(
            config["summoner_region"], summoner_id
        )

        return league_data[0]
    except ApiError as err:
        if err.response.status_code == 404:
            report_error("League data could not be found.")
        else:
            raise


def score_match(match_id: int) -> int:
    """Gathers summoner + team data for a single match
    Returns an overall match score
    """

    score = 0
    participant_id = 0
    team_id = 0
    summoner_stats = {}
    team_stats = {}
    match_data = get_match_data(match_id)
    game_minutes = match_data["gameDuration"] / 60

    for participant_identity in match_data["participantIdentities"]:
        if (
            participant_identity["player"]["summonerName"]
            == config["summoner_name"]
        ):
            participant_id = participant_identity["participantId"]

    if participant_id == 0:
        report_error("Participant data could not be found.")

    for participant in match_data["participants"]:
        if participant["participantId"] == participant_id:
            summoner_stats = participant["stats"]
            team_id = participant["teamId"]
            break

    if team_id == 0:
        report_error("Team data could not be found.")

    for team in match_data["teams"]:
        if team["teamId"] == team_id:
            team_stats = team

    if not summoner_stats:
        report_error("Summoner stats could not be found.")
    elif not team_stats:
        report_error("Team stats could not be found.")

    score += score_generic_match(summoner_stats, team_stats, game_minutes)

    return math.floor(score)


def score_generic_match(
    summoner_stats: dict, team_stats: dict, game_minutes: float
) -> float:
    """Generates a match score (regardless of role)"""

    match_score = 0

    # High value metrics
    # Win
    if team_stats["win"] == "Win":
        match_score += 200
    # KDA
    match_score += (
        (summoner_stats["kills"] + summoner_stats["assists"])
        / summoner_stats["deaths"]
    ) * 50
    # CS
    match_score += summoner_stats["totalMinionsKilled"]
    # Vision
    match_score += summoner_stats["visionScore"]
    # Gold per minute
    match_score += (summoner_stats["goldEarned"] / game_minutes) / 2
    # First tower (kill)
    if summoner_stats["firstTowerKill"]:
        match_score += 50
    # First tower (assist)
    if summoner_stats["firstTowerAssist"]:
        match_score += 25
    # Dragon kills
    match_score += team_stats["dragonKills"] * 10

    # Mid value metrics
    # Penta kills
    match_score += summoner_stats["pentaKills"] * 20
    # Quadra kills
    match_score += summoner_stats["quadraKills"] * 15
    # Triple kills
    match_score += summoner_stats["tripleKills"] * 10
    # Damage per minute
    match_score += (summoner_stats["totalDamageDealt"] / game_minutes) / 100
    # Healing per minute
    match_score += (summoner_stats["totalHeal"] / game_minutes) / 10
    # Baron kills
    match_score += team_stats["baronKills"] * 10
    # Heralds
    match_score += team_stats["riftHeraldKills"] * 10
    # Game speed
    if game_minutes < config["fast_game_minutes"]:
        match_score += 10

    # Low value metrics
    # Wards placed
    match_score += summoner_stats["wardsPlaced"] / 2
    # Wards killed
    match_score += summoner_stats["wardsKilled"] / 2
    # Towers
    match_score += team_stats["towerKills"]
    # First blood (kill)
    if summoner_stats["firstBloodKill"]:
        match_score += 3
    # First blood (assist)
    if summoner_stats["firstBloodAssist"]:
        match_score += 1
    # First inhibitor (kill)
    if summoner_stats["firstInhibitorKill"]:
        match_score += 3
    # First inhibitor (assist)
    if summoner_stats["firstInhibitorAssist"]:
        match_score += 2

    # Ranked tier multiplier
    match_score *= tier_multiplier()

    return match_score


def tier_multiplier() -> int:
    """Returns a multiplier based on summoner league"""

    summoner = get_summoner(config["summoner_name"])

    league_data = get_league_data(summoner["id"])

    tier_multipliers = {
        "challenger": 50,
        "grandmaster": 40,
        "master": 30,
        "diamond": 20,
        "platinum": 10,
        "gold": 7,
        "silver": 5,
        "bronze": 3,
        "iron": 2,
        "unranked": 1,
    }

    return tier_multipliers.get(league_data["tier"].lower())


def report_error(message: str) -> None:
    """Prints an error message and exits"""

    print("Error: {message}".format(message=message))
    sys.exit()


if __name__ == "__main__":
    rate_summoner()
