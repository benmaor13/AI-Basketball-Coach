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
        description="Indicates the game location. 'Home' means playing at the home_team's arena."
    )

    home_score: int = Field(..., ge=0, description="Total points scored by the home team.")
    away_score: int = Field(..., ge=0, description="Total points scored by the away team.")
    current_period: int = Field(..., ge=1, description="Current game period. e.g., 1-4 for quarters.")

    minutes_remaining: int = Field(..., ge=0, le=20, description="Minutes left on the clock.")
    seconds_remaining: int = Field(..., ge=0, le=59, description="Seconds left on the clock.")

    possession: Literal["Home", "Away", "Neutral"] = Field(default="Neutral")
    home_timeouts_remaining: int = Field(default=3, ge=0)
    away_timeouts_remaining: int = Field(default=3, ge=0)
    home_team_fouls: int = Field(default=0, ge=0)
    away_team_fouls: int = Field(default=0, ge=0)

    @model_validator(mode='after')
    def validate_game_logic(self) -> 'GameState':
        if self.minutes_remaining > self.rules.period_length_minutes:
            raise ValueError(
                f"Minutes remaining ({self.minutes_remaining}) cannot exceed "
                f"league period duration ({self.rules.period_length_minutes})"
            )

        if self.home_timeouts_remaining > self.rules.max_timeouts:
            raise ValueError(f"Home team has more timeouts than allowed")

        return self

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
                "rules": {
                    "league_format": "FIBA",
                    "number_of_periods": 4,
                    "period_length_minutes": 10,
                    "overtime_length_minutes": 5,
                    "max_fouls_per_player": 5,
                    "team_fouls_to_penalty": 4,
                    "shot_clock_seconds": 24,
                    "offensive_rebound_reset_seconds": 14,
                    "max_timeouts": 5
                },
                "momentum": {
                    "overall_trend": "Strong Home",
                    "home_team_run": 8,
                    "away_team_run": 0,
                    "crowd_intensity": "Electric"
                },
                "directives": {
                    "primary_strategy": "Pace and Space",
                    "defensive_focus": "Force Turnovers",
                    "risk_tolerance": "High",
                    "game_objective": "Win at all costs"
                },
                "home_team": {
                    "name": "BGU Lakers",
                    "league_position": 1,
                    "win_streak": 3,
                    "offensive_rank": 2,
                    "defensive_rank": 4,
                    "timeouts_remaining": 2,
                    "team_fouls": 3,
                    "upcoming_schedule_density": "High",
                    "players": [
                        {"name": "Noam", "age": 24, "number": 7, "position": "PG", "is_on_court": True, "current_fouls": 2, "minutes_played": 32, "fatigue_level": "Normal", "field_goals_made": 5, "field_goals_attempted": 10, "three_pointers_made": 2, "three_pointers_attempted": 4, "free_throws_made": 4, "free_throws_attempted": 4, "rebounds": 3, "assists": 8, "steals": 2, "blocks": 0, "turnovers": 3, "position_rank": 1},
                        {"name": "Ben", "age": 25, "number": 13, "position": "SG", "is_on_court": True, "current_fouls": 1, "minutes_played": 28, "fatigue_level": "Normal", "field_goals_made": 7, "field_goals_attempted": 14, "three_pointers_made": 4, "three_pointers_attempted": 8, "free_throws_made": 2, "free_throws_attempted": 2, "rebounds": 4, "assists": 2, "steals": 1, "blocks": 0, "turnovers": 1, "position_rank": 1},
                        {"name": "Guy", "age": 23, "number": 23, "position": "SF", "is_on_court": True, "current_fouls": 3, "minutes_played": 30, "fatigue_level": "Normal", "field_goals_made": 4, "field_goals_attempted": 9, "three_pointers_made": 1, "three_pointers_attempted": 3, "free_throws_made": 1, "free_throws_attempted": 2, "rebounds": 6, "assists": 3, "steals": 1, "blocks": 1, "turnovers": 2, "position_rank": 1},
                        {"name": "Dan", "age": 26, "number": 33, "position": "PF", "is_on_court": True, "current_fouls": 4, "minutes_played": 25, "fatigue_level": "Normal", "field_goals_made": 6, "field_goals_attempted": 8, "three_pointers_made": 0, "three_pointers_attempted": 0, "free_throws_made": 3, "free_throws_attempted": 5, "rebounds": 9, "assists": 1, "steals": 0, "blocks": 2, "turnovers": 1, "position_rank": 1},
                        {"name": "Tom", "age": 22, "number": 55, "position": "C", "is_on_court": True, "current_fouls": 2, "minutes_played": 35, "fatigue_level": "Normal", "field_goals_made": 8, "field_goals_attempted": 11, "three_pointers_made": 0, "three_pointers_attempted": 0, "free_throws_made": 4, "free_throws_attempted": 6, "rebounds": 12, "assists": 2, "steals": 0, "blocks": 4, "turnovers": 2, "position_rank": 1}
                    ]
                },
                "away_team": {
                    "name": "Away Town Ballers",
                    "league_position": 4,
                    "win_streak": -1,
                    "offensive_rank": 5,
                    "defensive_rank": 10,
                    "timeouts_remaining": 1,
                    "team_fouls": 5,
                    "upcoming_schedule_density": "Medium",
                    "players": [
                        {"name": "Alex", "age": 28, "number": 1, "position": "PG", "is_on_court": True, "current_fouls": 3, "minutes_played": 30, "fatigue_level": "Normal", "field_goals_made": 4, "field_goals_attempted": 12, "three_pointers_made": 1, "three_pointers_attempted": 5, "free_throws_made": 2, "free_throws_attempted": 2, "rebounds": 2, "assists": 6, "steals": 1, "blocks": 0, "turnovers": 4, "position_rank": 1},
                        {"name": "Mike", "age": 27, "number": 2, "position": "SG", "is_on_court": True, "current_fouls": 2, "minutes_played": 26, "fatigue_level": "Normal", "field_goals_made": 5, "field_goals_attempted": 10, "three_pointers_made": 2, "three_pointers_attempted": 6, "free_throws_made": 0, "free_throws_attempted": 0, "rebounds": 3, "assists": 1, "steals": 0, "blocks": 0, "turnovers": 1, "position_rank": 1},
                        {"name": "John", "age": 29, "number": 3, "position": "SF", "is_on_court": True, "current_fouls": 4, "minutes_played": 34, "fatigue_level": "Normal", "field_goals_made": 8, "field_goals_attempted": 16, "three_pointers_made": 3, "three_pointers_attempted": 7, "free_throws_made": 5, "free_throws_attempted": 6, "rebounds": 5, "assists": 4, "steals": 2, "blocks": 1, "turnovers": 3, "position_rank": 1},
                        {"name": "Chris", "age": 24, "number": 4, "position": "PF", "is_on_court": True, "current_fouls": 5, "minutes_played": 22, "fatigue_level": "Normal", "field_goals_made": 3, "field_goals_attempted": 7, "three_pointers_made": 0, "three_pointers_attempted": 1, "free_throws_made": 1, "free_throws_attempted": 2, "rebounds": 7, "assists": 0, "steals": 0, "blocks": 0, "turnovers": 1, "position_rank": 1},
                        {"name": "Sam", "age": 30, "number": 5, "position": "C", "is_on_court": True, "current_fouls": 3, "minutes_played": 28, "fatigue_level": "Normal", "field_goals_made": 4, "field_goals_attempted": 9, "three_pointers_made": 0, "three_pointers_attempted": 0, "free_throws_made": 2, "free_throws_attempted": 4, "rebounds": 10, "assists": 1, "steals": 1, "blocks": 2, "turnovers": 2, "position_rank": 1}
                    ]
                }
            }
        }
    )