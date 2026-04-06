import copy
import pytest
from pydantic import ValidationError
from app.models.game_momentum import GameMomentum
from app.models.team import Team
from app.models.league_rules import LeagueRules
from app.models.game_state import GameState
from app.models.examples import GAME_STATE_EXAMPLE


def test_simultaneous_runs_rejected():
    """
    Both teams cannot be on a scoring run simultaneously.
    Tests the custom model_validator in GameMomentum.
    """
    # expecting an error to arise
    with pytest.raises(ValidationError):
        GameMomentum(
            overall_trend="Neutral",
            home_team_run=5,
            away_team_run=5,
            crowd_intensity="Engaged"
        )


def test_team_wrong_number_on_court():
    """
    Team with 4 players on court should fail validation.
    Tests the custom model_validator in Team.
    """
    # adding 4 players to the court
    players = []
    for i in range(4):
        players.append({
            "name": f"Player{i}",
            "age": 24,
            "number": i + 1,
            "position": "PG",
            "position_rank": 1,
            "style": "Floor General",
            "season_ft_pct": 80,
            "is_on_court": True
        })
    # adding players to the bench
    for i in range(3):
        players.append({
            "name": f"Bench{i}",
            "age": 24,
            "number": i + 10,
            "position": "PG",
            "position_rank": 2,
            "style": "Versatile",
            "season_ft_pct": 70,
            "is_on_court": False
        })
    # expecting a specific error
    with pytest.raises(ValidationError) as exc_info:
        Team(name="Test Team", players=players)
    assert "5 players" in str(exc_info.value)


def test_fouled_out_player_on_court_rejected():
    """
    A player who has fouled out cannot be marked is_on_court=True.
    Tests the cross-model validation in GameState.
    """
    bad_example = copy.deepcopy(GAME_STATE_EXAMPLE)
    # Ronen Bar (#11) is on court — give him max fouls (FIBA = 5)
    for player in bad_example["home_team"]["players"]:
        if player["number"] == 11:
            player["current_fouls"] = 5
            break
    # expecting an error
    with pytest.raises(ValidationError):
        GameState(**bad_example)


def test_timeouts_exceed_maximum_rejected():
    """
    Timeouts remaining cannot exceed the league maximum.
    Tests the cross-model validation in GameState.
    """
    bad_example = copy.deepcopy(GAME_STATE_EXAMPLE)
    bad_example["home_timeouts_remaining"] = 99
    # expecting an error
    with pytest.raises(ValidationError):
        GameState(**bad_example)


def test_fiba_rules_override():
    """
    FIBA format must override all manually set fields with official values.
    Tests the model_validator in LeagueRules.
    """
    rules = LeagueRules(
        league_format="FIBA",
        number_of_periods=2,       # wrong — should become 4
        period_length_minutes=12,  # wrong — should become 10
        max_fouls_per_player=6     # wrong — should become 5
    )
    # checking the fields
    assert rules.number_of_periods == 4
    assert rules.period_length_minutes == 10
    assert rules.max_fouls_per_player == 5
    assert rules.max_timeouts == 5


def test_nba_rules_override():
    """
    NBA format must override all manually set fields with official values.
    Tests the model_validator in LeagueRules.
    """
    rules = LeagueRules(
        league_format="NBA",
        period_length_minutes=10,  # wrong — should become 12
        max_fouls_per_player=5     # wrong — should become 6
    )
    # checking the fields
    assert rules.period_length_minutes == 12
    assert rules.max_fouls_per_player == 6
    assert rules.max_timeouts == 7