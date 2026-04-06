import pytest
from app.models.game_state import GameState
from app.models.examples import GAME_STATE_EXAMPLE


@pytest.fixture
def valid_state():
    """A fully valid GameState built from GAME_STATE_EXAMPLE."""
    # Dictionary Unpacking
    return GameState(**GAME_STATE_EXAMPLE)