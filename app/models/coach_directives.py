from pydantic import BaseModel, Field
from typing import Literal


class CoachDirectives(BaseModel):
    """
    Strategic goals and tactical constraints set by the coach.
    """

    primary_strategy: Literal["Pace and Space", "Grind it Out", "Inside-Out", "Perimeter Focus", "Balanced"] = Field(
        default="Balanced",
        description="The main offensive philosophy to enforce",
        json_schema_extra={"example": "Pace and Space"}
    )

    defensive_focus: Literal[
        "Protect the Paint", "Pressure Guards", "Switch Everything", "Zone Defense", "Man-to-Man"] = Field(
        default="Man-to-Man",
        description="The primary defensive scheme to execute",
        json_schema_extra={"example": "Protect the Paint"}
    )

    risk_tolerance: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="How much risk the AI should take in its recommendations (e.g., gambling on steals)",
        json_schema_extra={"example": "High"}
    )

    game_objective: Literal["Win at all costs", "Develop young players", "Protect lead", "Aggressive Comeback"] = Field(
        default="Win at all costs",
        description="The overarching goal for the current phase of the game",
        json_schema_extra={"example": "Aggressive Comeback"}
    )

