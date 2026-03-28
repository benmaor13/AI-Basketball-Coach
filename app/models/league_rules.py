from pydantic import BaseModel, Field, model_validator
from typing import Literal


class LeagueRules(BaseModel):
    """
    the rules and specific relevant details for the league where the game is played
    """

    league_format: Literal["FIBA", "NBA", "NCAA", "Custom"] = Field(
        default="FIBA",
        description="Select league. For NBA/FIBA/NCAA, all fields will be override, select costume if you want to choose something different",
        json_schema_extra={"example": "NBA"}
    )

    number_of_periods: int = Field(default=4, ge=1, le=4)
    period_length_minutes: int = Field(default=10, ge=5, le=20)
    overtime_length_minutes: int = Field(default=5, ge=2, le=5)
    max_fouls_per_player: int = Field(default=5, ge=4, le=6)
    team_fouls_to_penalty: int = Field(default=4, ge=1, le=7)
    shot_clock_seconds: int = Field(default=24, ge=12, le=35)
    offensive_rebound_reset_seconds: int = Field(default=14, ge=12, le=35)

    @model_validator(mode='after')
    def enforce_league_rules(self) -> LeagueRules:
        """
        Overrides manual input with official rules for standard formats.
        """
        if self.league_format == "NBA":
            self.number_of_periods = 4
            self.period_length_minutes = 12
            self.max_fouls_per_player = 6
            self.team_fouls_to_penalty = 4
            self.shot_clock_seconds = 24
            self.offensive_rebound_reset_seconds = 14

        elif self.league_format == "FIBA":
            self.number_of_periods = 4
            self.period_length_minutes = 10
            self.max_fouls_per_player = 5
            self.team_fouls_to_penalty = 4
            self.shot_clock_seconds = 24
            self.offensive_rebound_reset_seconds = 14

        elif self.league_format == "NCAA":
            self.number_of_periods = 2
            self.period_length_minutes = 20
            self.max_fouls_per_player = 5
            self.team_fouls_to_penalty = 6
            self.shot_clock_seconds = 30
            self.offensive_rebound_reset_seconds = 20

        return self