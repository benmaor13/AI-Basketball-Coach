from pydantic import BaseModel, Field, computed_field
from typing import Literal


class Player(BaseModel):
    # Identity fields
    name: str = Field(
        ...,
        json_schema_extra={"example": "Noam"}
    )
    age: int = Field(
        ...,
        ge=15,
        le=60,
        description="15 to 60",
        json_schema_extra={"example": 24}
    )
    number: int = Field(
        ...,
        ge=0,
        le=99,
        json_schema_extra={"example": 7}
    )
    position: Literal["PG", "SG", "SF", "PF", "C"] = Field(
        ...,
        description="Basketball position(PG, SG, SF, PF, C)",
        json_schema_extra={"example": "PG"}
    )
    position_rank: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Rank in this position from all team players (1 is best)",
        json_schema_extra={"example": 1}
    )

    # real time data
    is_on_court: bool = Field(default=False)
    minutes_played: int = Field(
        default=0,
        ge=0,
        le=48,
        json_schema_extra={"example": 12}
    )
    fatigue_level: Literal["Fresh", "Normal", "Tired", "Exhausted", "Injured"] = Field(
        default="Fresh",
        description="describe the fatigue level (also you can enter Injured)",
        json_schema_extra = {"example": 12}
    )
    current_fouls: int = Field(
        default=0,
        ge=0,
        le=6,
        json_schema_extra={"example": 2}
    )
    field_goals_made: int = Field(default=0, ge=0)
    field_goals_attempted: int = Field(default=0, ge=0)
    three_pointers_made: int = Field(default=0, ge=0)
    three_pointers_attempted: int = Field(default=0, ge=0)
    free_throws_made: int = Field(default=0, ge=0)
    free_throws_attempted: int = Field(default=0, ge=0)
    rebounds: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    steals: int = Field(default=0, ge=0)
    blocks: int = Field(default=0, ge=0)
    turnovers: int = Field(default=0, ge=0)

    # computed properties
    @computed_field
    @property
    def field_goal_percentage(self) -> float:
        total_attempted = self.field_goals_attempted + self.three_pointers_attempted
        if total_attempted == 0:
            return 0.0
        total_made = self.field_goals_made + self.three_pointers_made
        return round((total_made / total_attempted) * 100, 1)

    @computed_field
    @property
    def three_point_percentage(self) -> float:
        if self.three_pointers_attempted == 0:
            return 0.0
        return round((self.three_pointers_made / self.three_pointers_attempted) * 100, 1)

    @computed_field
    @property
    def free_throws_percentage(self) -> float:
        if self.free_throws_attempted == 0:
            return 0.0
        return round((self.free_throws_made / self.free_throws_attempted) * 100, 1)