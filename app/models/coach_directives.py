from pydantic import BaseModel, Field
from typing import Literal


class CoachDirectives(BaseModel):
    """
    Strategic goals and tactical beliefs of the coach.
    """

    offensive_strategy: Literal[
        "Pace & Space",
        "Attack the Paint",
        "Pick & Roll Heavy",
        "Feed the Post",
        "Motion Offense"
    ] = Field(
        default="Motion Offense",
        description="The offensive mechanism the coach wants to run."
    )

    defensive_focus: Literal[
        "Protect the Paint",
        "Deny Perimeter",
        "Blitz & Trap",
        "Switch Everything",
        "Zone Defense"
    ] = Field(
        default="Protect the Paint",
        description="The defensive scheme the coach wants to apply."
    )

    risk_tolerance: Literal[
        "Low",
        "Medium",
        "High"
    ] = Field(
        default="Medium",
        description="Governs AI thresholds for fatigue and foul trouble decisions."
    )

    game_objective: Literal[
        "Win Now",
        "Develop Youth",
        "Kill the Clock",
        "Desperate Comeback"
    ] = Field(
        default="Win Now",
        description="The current meta-goal that drives the AI's overall priority logic."
    )