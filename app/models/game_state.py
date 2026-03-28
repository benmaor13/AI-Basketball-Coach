from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

from .team import Team
from .league_rules import LeagueRules
from .game_momentum import GameMomentum
from .coach_directives import CoachDirectives


class GameState(BaseModel):
    """
    Groups all real-time data for AI tactical analysis.
    """
    # nested objects
    home_team: Team
    away_team: Team
    rules: LeagueRules
    momentum: GameMomentum
    directives: CoachDirectives

    # data about the current circumstances
    venue_type: Literal["Home", "Away", "Neutral"] = Field(
        ...,
        description="Indicates the game location. 'Home' means playing at the home_team's arena.",
        json_schema_extra={"example": "Home"}
    )

    home_score: int = Field(
        ...,
        ge=0,
        description="Total points scored by the home team.",
        json_schema_extra={"example": 88}
    )

    away_score: int = Field(
        ...,
        ge=0,
        description="Total points scored by the away team.",
        json_schema_extra={"example": 82}
    )

    current_period: int = Field(
        ...,
        ge=1,
        description="Current game period. e.g., 1-4 for quarters. 5+ indicates Overtime (OT).",
        json_schema_extra={"example": 4}
    )

    minutes_remaining: int = Field(
        ...,
        ge=0,
        le=20,
        description="Minutes left on the clock for this period.",
        json_schema_extra={"example": 3}
    )

    seconds_remaining: int = Field(
        ...,
        ge=0,
        le=59,
        description="Seconds left on the clock for this minute.",
        json_schema_extra={"example": 45}
    )

    possession: Literal["Home", "Away", "Neutral"] = Field(
        default="Neutral",
        description="Which team currently holds the ball.",
        json_schema_extra={"example": "Home"}
    )

    home_timeouts_remaining: int = Field(
        default=3,
        ge=0,
        description="Number of timeouts currently available for the home team.",
        json_schema_extra={"example": 2}
    )

    away_timeouts_remaining: int = Field(
        default=3,
        ge=0,
        description="Number of timeouts currently available for the away team.",
        json_schema_extra={"example": 1}
    )

    home_team_fouls: int = Field(
        default=0,
        ge=0,
        description="Total fouls committed by the home team in the current period.",
        json_schema_extra={"example": 3}
    )

    away_team_fouls: int = Field(
        default=0,
        ge=0,
        description="Total fouls committed by the away team in the current period.",
        json_schema_extra={"example": 5}
    )

    # validation of the timeouts and time remaining according to the league's rules
    @model_validator(mode='after')
    def validate_game_logic(self) -> GameState:
        if self.minutes_remaining > self.rules.period_duration:
            raise ValueError(
                f"Minutes remaining ({self.minutes_remaining}) cannot exceed "
                f"league period duration ({self.rules.period_duration})"
            )

        if self.home_timeouts_remaining > self.rules.max_timeouts:
            raise ValueError(f"Home team has more timeouts than allowed in {self.rules.league_name}")

        return self

    # configuration for better experience using the swagger and also for the performance of AI
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "venue_type": "Home",
                "home_score": 88,
                "away_score": 82,
                "current_period": 4,
                "minutes_remaining": 3,
                "seconds_remaining": 45,
                "possession": "Home",
                "home_timeouts_remaining": 2,
                "away_timeouts_remaining": 1,
                "home_team_fouls": 3,
                "away_team_fouls": 5,
                "home_team": {
                    "name": "Home City Hoopers",
                    "coach_name": "Coach A",
                    "players_on_court": [
                        {"jersey_number": 23, "position": "SF", "points": 25, "fouls": 2},
                        {"jersey_number": 1, "position": "PG", "points": 12, "fouls": 3}
                    ]
                },
                "away_team": {
                    "name": "Away Town Ballers",
                    "coach_name": "Coach B",
                    "players_on_court": [
                        {"jersey_number": 30, "position": "PG", "points": 32, "fouls": 1}
                    ]
                },
                "rules": {
                    "league_name": "FIBA",
                    "period_duration": 10,
                    "max_timeouts": 5
                },
                "momentum": {
                    "home_team_run": 8,
                    "away_team_run": 0,
                    "description": "Home team is on an 8-0 run, crowd is heavily involved."
                },
                "directives": {
                    "offensive_focus": "Attack the paint",
                    "defensive_focus": "No threes"
                }
            }
        }
    )