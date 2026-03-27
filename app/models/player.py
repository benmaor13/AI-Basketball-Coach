from pydantic import BaseModel, Field
from typing import Literal

class Player(BaseModel):
    """
    Model representing a basketball player, including identity,
    real-time status, and performance stats.
    """
    # --- Identity ---
    name: str = Field(
        ...,
        description="Player's full name",
        json_schema_extra={"example": "Noam"}
    )
    age: int = Field(
        ...,
        ge=15, le=50,
        description="Player's age (range 15-50)",
        json_schema_extra={"example": 24}
    )
    number: int = Field(
        ...,
        ge=0, le=99,
        description="Jersey number (0-99)",
        json_schema_extra={"example": 7}
    )
    position: Literal["PG", "SG", "SF", "PF", "C"] = Field(
        ...,
        description="Basketball position: PG (Point Guard), SG (Shooting Guard), SF (Small Forward), PF (Power Forward), C (Center)",
        json_schema_extra={"example": "PG"}
    )
    position_rank: int = Field(
        default=1,
        ge=1, le=5,
        description="Rank in this position from all the players in the team(1 means the best)",
        json_schema_extra={"example": 1}
    )

    # --- Real-Time Physical Status ---
    is_on_court: bool = Field(
        default=False,
        description="Whether the player is currently active on the floor"
    )
    minutes_played: int = Field(
        default=0,
        ge=0, le=48,
        description="Total minutes played in the current game",
        json_schema_extra={"example": 12}
    )
    fatigue_level: Literal["Fresh", "Normal", "Tired", "Exhausted", "Injured"] = Field(
        default="Fresh",
        description="Current physical conditioning impact(you can enter also Injured if he got Injured"
    )

    # --- Live Box Score Stats (The "Engine" Data) ---
    current_points: int = Field(
        default=0, ge=0,
        description="Points scored in the current game",
        json_schema_extra={"example": 14}
    )
    current_fouls: int = Field(
        default=0, ge=0, le=6,
        description="Current foul count(0-6 because of Nba)",
        json_schema_extra={"example": 2}
    )
    number_of_shots:int= Field(
        default=0,ge=0,
        description="Total number of shots",
        json_schema_extra={"example": 2}
    )
    accuracy_percentage: float = Field(
        default=0, ge=0,
        description="scoring percentage",
        json_schema_extra={"example": 2}
    )
    rebounds: int = Field(default=0, ge=0, description="Total rebounds (Offensive + Defensive)")
    assists: int = Field(default=0, ge=0, description="Total assists")
    steals: int = Field(default=0, ge=0, description="Total steals")
    blocks: int = Field(default=0, ge=0, description="Total blocks")
    turnovers: int = Field(default=0, ge=0, description="Total ball turnovers")