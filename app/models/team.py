from pydantic import BaseModel, Field
from typing import List, Literal
from .player import Player


class Team(BaseModel):
    """
    Comprehensive model for a basketball team, including roster,
    real-time strategic context, and performance trends.
    """


    name: str = Field(
        ...,
        description="The team's official name",
        json_schema_extra={"example": "BGU Lakers"}
    )

    players: List[Player] = Field(
        ...,
        min_length=5,
        max_length=15,
        description="Full roster of the team (must have 5-15 players)"
    )

    active_lineup: List[Player] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="The 5 players currently active on the court"
    )


    league_position: int = Field(
        default=1,
        ge=1,
        description="Current standing in the league (1 is the top-seeded team)",
        json_schema_extra={"example": 3}
    )

    win_streak: int = Field(
        default=0,
        description="Current performance trend: positive for wins (e.g., 5), negative for losses (e.g., -3)",
        json_schema_extra={"example": 4}
    )

    offensive_rank: int = Field(
        default=10,
        ge=1,
        description="Team's offensive efficiency rank in the league (1 is the best/highest)",
        json_schema_extra={"example": 2}
    )

    defensive_rank: int = Field(
        default=10,
        ge=1,
        description="Team's defensive efficiency rank in the league (1 is the best/highest)",
        json_schema_extra={"example": 5}
    )


    timeouts_remaining: int = Field(
        default=3,
        ge=0,
        description="Number of timeouts the coach can still use",
        json_schema_extra={"example": 2}
    )

    team_fouls: int = Field(
        default=0,
        ge=0,
        description="Total fouls committed by the team in the current quarter",
        json_schema_extra={"example": 3}
    )


    play_style: Literal["Run and Gun", "Pick and Roll", "Defensive", "Pace and Space", "Balanced"] = Field(
        default="Balanced",
        description="The primary tactical approach of the team",
        json_schema_extra={"example": "Pace and Space"}
    )

    upcoming_schedule_density: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="How crowded the team's schedule is (affects fatigue management)",
        json_schema_extra={"example": "High"}
    )