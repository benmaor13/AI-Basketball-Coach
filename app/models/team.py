from pydantic import BaseModel, Field, computed_field, model_validator
from typing import List, Literal
from .player import Player


class Team(BaseModel):
    """
    model for a basketball team
    """

    # identity properties
    name: str = Field(
        ...,
        description="The team's official name",
        json_schema_extra={"example": "BGU Lakers"}
    )

    players: List[Player] = Field(
        ...,
        min_length=5,
        max_length=15,
        description="Full roster of the team (must contain between 5 to 15 players)",
    )

    # Performance Properties
    league_position: int = Field(
        default=1,
        ge=1,
        description="Current standing in the league(1 is the first in the league)",
        json_schema_extra={"example": 1}
    )

    win_streak: int = Field(
        default=0,
        description="Current win streak. Positive integers for wins streak (e.g., 5), negative for losses streak(e.g., -3).",
        json_schema_extra={"example": 3}
    )

    offensive_rank: int = Field(
        default=5,
        ge=1,
        description="Team's offensive efficiency rank in the league. 1 is the most efficient team.",
        json_schema_extra={"example": 4}
    )

    defensive_rank: int = Field(
        default=10,
        ge=1,
        description="Team's defensive efficiency rank in the league. 1 is the best defensive team.",
        json_schema_extra={"example": 7}
    )

    # game real time state
    timeouts_remaining: int = Field(
        default=3,
        ge=0,
        description="Number of remaining timeouts available for the coach.",
        json_schema_extra={"example": 2}
    )

    team_fouls: int = Field(
        default=0,
        ge=0,
        description="Total team fouls committed in the current period.",
        json_schema_extra={"example": 2}
    )

    upcoming_schedule_density: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="Frequency of recent and upcoming games(Low, Medium, High)",
        json_schema_extra={"example": "High"}
    )

    # computed properties
    @computed_field
    @property
    def active_lineup(self) -> List[Player]:
        """
        Dynamically calculates the active 5-man lineup from the players roster
        based on their 'is_on_court' status.
        """
        return [p for p in self.players if p.is_on_court]

    @model_validator(mode='after')
    def validate_active_lineup_size(self) -> 'Team':
        """
        ensures exactly 5 players on the court
        """
        # counting the number of players on the court
        active_count = len(self.active_lineup)
        # handling the case of a wrong number
        if active_count != 5:
            raise ValueError(
                f"Invalid game state: {active_count} players marked as on-court. "
                "A basketball team must have exactly 5 players active."
            )

        return self