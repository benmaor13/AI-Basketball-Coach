from pydantic import BaseModel, Field
from typing import Literal


class LeagueRules(BaseModel):
    """
    Defines the regulatory environment of the match.
    These constraints help the AI understand the pacing and rules of the specific league.
    """
    league_format: Literal["FIBA", "NBA", "NCAA", "EuroLeague", "3x3"] = Field(
        default="FIBA",
        description="League format",
        json_schema_extra={"example": "FIBA"}
    )

    number_of_periods: int = Field(
        default=4,
        ge=1,
        le=4,
        description="Number of standard periods in the game (e.g.,4 quarters or 2 halves)",
        json_schema_extra={"example": 4}
    )
    period_length_minutes: int = Field(
        default=10,
        ge=8,
        le=20,
        description="Duration of a single period in minutes",
        json_schema_extra={"example": 10}
    )
    overtime_length_minutes: int = Field(
        default=5,
        ge=2,
        le=5,
        description="Duration of an overtime period in minutes",
        json_schema_extra={"example": 5}
    )

    max_fouls_per_player: int = Field(
        default=5,
        ge=4,
        le=6,
        description="Number of personal fouls before a player is disqualified",
        json_schema_extra={"example": 5}
    )
    team_fouls_to_penalty: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of team fouls in a period before the opposing team shoots free throws",
        json_schema_extra={"example": 4}
    )

    shot_clock_seconds: int = Field(
        default=24,
        ge=12,
        le=30,
        description="Duration of the shot clock in seconds",
        json_schema_extra={"example": 24}
    )
    offensive_rebound_reset_seconds: int = Field(
        default=14,
        ge=12,
        le=30,
        description="Shot clock reset duration after an offensive rebound",
        json_schema_extra={"example": 14}
    )