from pydantic import BaseModel, Field
from typing import Literal

class CoachDirectives(BaseModel):
    """
    Strategic goals and tactical beliefs of the coach.
    The literals act as explicit commands for the AI's action_type and stat prioritization.
    """

    offensive_strategy: Literal[
        "Pace & Space (Sub in highest 3PT%, push fast breaks)",
        "Attack the Paint (Drive to rim, exploit Penalty, target opponents with fouls)",
        "Pick & Roll Heavy (Pair highest EFF PG with highest EFF Center)",
        "Feed the Post (Isolate highest EFF Center/PF inside the paint)",
        "Motion Offense (Balance floor, prioritize overall team EFF)"
    ] = Field(
        default="Motion Offense (Balance floor, prioritize overall team EFF)",
        description="The precise offensive mechanism. Tells the AI exactly which stats/player types to prioritize."
    )

    defensive_focus: Literal[
        "Protect the Paint (Sub in high BLK players, drop coverage, prevent layups)",
        "Deny Perimeter (Sub fast guards, hug shooters, run them off the 3PT line)",
        "Blitz & Trap (Force Turnovers, double-team ball handlers, sub high STL players)",
        "Switch Everything (Versatile lineup, sub out slow/heavy Centers)",
        "Zone Defense (2-3 Zone: Clog the paint, prioritize size, mitigate player fatigue)"
    ] = Field(
        default="Protect the Paint (Sub in high BLK players, drop coverage, prevent layups)",
        description="The specific defensive scheme. Dictates player subs based on defensive stats (Blocks, Steals, Mobility)."
    )

    risk_tolerance: Literal[
        "Low (MUST sub out Tired or Foul Trouble players immediately)",
        "Medium (Standard logic: rest role players, stretch Rank-1 stars slightly)",
        "High (Keep Rank-1 stars on court regardless of Fatigue or Foul Trouble)"
    ] = Field(
        default="Medium (Standard logic: rest role players, stretch Rank-1 stars slightly)",
        description="Governs AI thresholds for fatigue and foul trouble alerts."
    )

    game_objective: Literal[
        "Win Now (Maximize current floor EFF and strictly play top Rank players)",
        "Develop Youth (Mandatory: Sub in U25 players, tolerate lower EFF for growth)",
        "Kill the Clock (Slow Pace, sub in highest FT% players and best perimeter defenders)",
        "Desperate Comeback (Max Pace, shoot quick 3s, use Foul Strategy to stop clock)"
    ] = Field(
        default="Win Now (Maximize current floor EFF and strictly play top Rank players)",
        description="The current meta-goal that drastically alters the AI's logic and priority scoring."
    )