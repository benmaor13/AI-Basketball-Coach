import copy
import pytest
from app.models.game_state import GameState
from app.models.examples import GAME_STATE_EXAMPLE


def test_clutch_time_triggers_correctly():
    """
    Under 2 minutes, last period, score within threshold
    should be detected as CLUTCH TIME.
    Tests _compute_game_flags() in GameState.
    """
    clutch_example = copy.deepcopy(GAME_STATE_EXAMPLE)
    clutch_example["minutes_remaining"] = 1
    clutch_example["seconds_remaining"] = 30
    clutch_example["home_score"] = 85
    clutch_example["away_score"] = 82  # diff = 3

    state = GameState(**clutch_example)
    flags = state._compute_game_flags()
    # checking whether it recognized that we are in clutch time
    assert flags["is_clutch_time"] is True


def test_regular_flow_when_lead_is_comfortable():
    """
    A comfortable lead should produce Regular Flow — not clutch time
    or late close game.
    Tests _compute_game_flags() in GameState.
    """
    comfortable_example = copy.deepcopy(GAME_STATE_EXAMPLE)
    comfortable_example["home_score"] = 95
    comfortable_example["away_score"] = 60  # 35 point lead

    state = GameState(**comfortable_example)
    flags = state._compute_game_flags()

    assert flags["is_clutch_time"] is False
    assert flags["is_late_close_game"] is False


def test_game_state_example_is_valid():
    """
    GAME_STATE_EXAMPLE must pass full validation without errors.
    Basic test to make sure the basic example is valid
    """
    state = GameState(**GAME_STATE_EXAMPLE)
    assert state.home_score == 88
    assert state.away_score == 82
    assert len(state.home_team.active_lineup) == 5
    assert len(state.away_team.active_lineup) == 5