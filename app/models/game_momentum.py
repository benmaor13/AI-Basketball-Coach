from pydantic import BaseModel, Field, model_validator
from typing import Literal
from app.core.constants import SIGNIFICANT_RUN_THRESHOLD
class GameMomentum(BaseModel):
    """
    some properties to identify psychological effects on the game
    like the crowd which has impact on the players.
    """
    overall_trend: Literal["Strong Home", "Slight Home", "Neutral", "Slight Away", "Strong Away"] = Field(
        default="Neutral",
        description="Who currently controls the energy and pace of the game(from the options Strong/Slight Home and Slight/Strong Away",
        json_schema_extra={"example": "Strong Home"}
    )
    # used to validate the overall_trend
    home_team_run: int = Field(
        default=0,
        ge=0,
        le=50,
        description=(
            "Recent scoring advantage for the home team — the difference between "
            "home points and away points in recent possessions. Not necessarily a "
            "shutout run. Used to indicate momentum direction and magnitude."
        )
    )
    # used to validate the overall_trend
    away_team_run: int = Field(
        default=0,
        ge=0,
        le=50,
        description=(
            "Recent scoring advantage for the away team — the difference between "
            "home points and away points in recent possessions. Not necessarily a "
            "shutout run. Used to indicate momentum direction and magnitude."
        )
    )
    crowd_intensity: Literal["Quiet", "Engaged", "Hostile", "Electric"] = Field(
        default="Engaged",
        description="The atmosphere in the arena(Quiet, Engaged, Hostile,or Electric)",
        json_schema_extra={"example": "Electric"}
    )

    @model_validator(mode='after')
    def validate_momentum_logic(self) -> 'GameMomentum':
        """
        Validates following things:
        1.Teams cannot be on simultaneous scoring runs.
        2.contradictions between runs and overall trend
        """
        if self.home_team_run > 0 and self.away_team_run > 0:
            raise ValueError(
                f"Conflicting state: Home run ({self.home_team_run}) and Away run ({self.away_team_run}). "
                "Only one team can have a scoring run."
            )

        if self.home_team_run >= SIGNIFICANT_RUN_THRESHOLD and self.overall_trend in ["Slight Away", "Strong Away", "Neutral"]:
            raise ValueError(
                f"Contradiction: Home team is on a {self.home_team_run}run, "
                f"but momentum trend is set to '{self.overall_trend}'. "
                "Trend must  favor the home team during a significant home run."
            )

        if self.away_team_run >= SIGNIFICANT_RUN_THRESHOLD and self.overall_trend in ["Slight Home", "Strong Home", "Neutral"]:
            raise ValueError(
                f"Contradiction: Away team is on a {self.away_team_run} run, "
                f"but momentum trend is set to '{self.overall_trend}'. "
                "Trend must  favor the away team during a significant away run."
            )

        return self