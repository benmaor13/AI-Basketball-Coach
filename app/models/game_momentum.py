from pydantic import BaseModel, Field
from typing import Literal


class GameMomentum(BaseModel):
    """
    Momentum of the game, helps deciding on the next steps
    """

    overall_trend: Literal["Strong Home", "Slight Home", "Neutral", "Slight Away", "Strong Away"] = Field(
        default="Neutral",
        description="Who currently controls the energy and pace of the game",
        json_schema_extra={"example": "Strong Home"}
    )

    home_team_run: int = Field(
        default=0,
        ge=0,
        description="Current unanswered points by the home team",
        json_schema_extra={"example": 8}
    )
    away_team_run: int = Field(
        default=0,
        ge=0,
        description="Current unanswered points by the away team",
        json_schema_extra={"example": 0}
    )

    crowd_intensity: Literal["Quiet", "Engaged", "Hostile", "Electric"] = Field(
        default="Engaged",
        description="The atmosphere in the arena, affecting player focus and pressure",
        json_schema_extra={"example": "Electric"}
    )

