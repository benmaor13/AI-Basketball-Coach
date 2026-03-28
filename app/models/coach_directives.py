from pydantic import BaseModel, Field
from typing import Literal

class CoachDirectives(BaseModel):
    """
    Strategic goals and tactical beliefs of the coach
    """

    primary_strategy: Literal["Pace and Space", "Grind it Out", "Inside-Out", "Perimeter Focus", "Balanced"] = Field(
        default="Balanced",
        description="The coach's main offensive philosophy the coach wants to enforce right now."
        "[Pace and Space, Grind it Out, Inside-Out, Perimeter Focus, Balanced]",
        json_schema_extra={"example": "Pace and Space"}
    )

    defensive_focus: Literal["Protect the Paint", "Pressure Perimeter", "Force Turnovers", "Conservative", "Switch Everything"] = Field(
        default="Protect the Paint",
        description="The primary defensive goal or scheme to execute right now."
        "[Protect the Paint, Pressure Perimeter, Force Turnovers, Conservative, Switch Everything]",
        json_schema_extra={"example": "Force Turnovers"}
    )

    risk_tolerance: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="AI constraint: Low (safe, high percentage plays), High (gambles, aggressive subs).",
        json_schema_extra={"example": "High"}
    )

    game_objective: Literal["Win at all costs", "Develop young players", "Protect lead", "Aggressive Comeback"] = Field(
        default="Win at all costs",
        description="goal for the current phase\maybe all game. Drastically alters the AI's decisions logic.",
        json_schema_extra={"example": "Aggressive Comeback"}
    )