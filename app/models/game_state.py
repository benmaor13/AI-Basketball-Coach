from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

from .team import Team
from .league_rules import LeagueRules
from .game_momentum import GameMomentum
from .coach_directives import CoachDirectives
from .examples import GAME_STATE_EXAMPLE


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

    # data about the current location of the game
    venue_type: Literal["Home", "Away", "Neutral"] = Field(
        ...,
        description="Indicates the game location. 'Home' means playing at the home_team's arena."
    )
    target_team: Literal["Home", "Away"] = Field(
        default="Home",
        description="The team the AI is currently coaching."
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
        """
        Validates the integrity of the game state, including timeouts,
        period timing (handling overtime), and foul rules.
        """
        # Timeouts Validation
        if self.home_timeouts_remaining > self.rules.max_timeouts or \
                self.away_timeouts_remaining > self.rules.max_timeouts:
            raise ValueError(f"A team cannot have more than {self.rules.max_timeouts} timeouts.")

        # Period and Time Validation (Handling Overtime vs. Regular periods)
        is_overtime = self.current_period > self.rules.number_of_periods
        max_minutes_for_period = self.rules.overtime_length_minutes if is_overtime else self.rules.period_length_minutes

        if self.minutes_remaining > max_minutes_for_period:
            raise ValueError(
                f"Invalid time: Minutes remaining ({self.minutes_remaining}) cannot exceed "
                f"the maximum length for period {self.current_period} ({max_minutes_for_period} mins)."
            )

        # Foul Validation (Data Integrity vs. Game Logic)
        max_fouls = self.rules.max_fouls_per_player
        for team in [self.home_team, self.away_team]:
            for player in team.players:
                # a player cannot have more that the maximum fouls
                if player.current_fouls > max_fouls:
                    raise ValueError(
                        f"Data Error: Player '{player.name}' ({team.name}) has {player.current_fouls} fouls, "
                        f"which exceeds the absolute league limit of {max_fouls}."
                    )
                # a player that plays now must have less fouls than the maximum
                if player.is_on_court and player.current_fouls >= max_fouls:
                    raise ValueError(
                        f"Game Logic Error: Player '{player.name}' is on court but has already "
                        f"fouled out ({player.current_fouls}/{max_fouls} fouls)."
                    )

        return self

    def to_ai_summary(self) -> str:
        """
        Sending the AI relevant information in a way it will give the most accurate answer
        and also making it shorter as possible to save tokens and minimize unrelevant info that can
        make the AI hallucinate
        """
        # Helper function to ensure unique player identification
        def fmt_p(p) -> str:
            return f"{p.name} (#{p.number})"

        summary = []
        # which team is the coach's team
        my_team = self.home_team if self.target_team == "Home" else self.away_team
        opp_team = self.away_team if self.target_team == "Home" else self.home_team
        # giving the AI info about the score situation with minimum letters
        score_diff = abs(self.home_score - self.away_score)
        if self.home_score == self.away_score:
            lead_status = "Game is TIED"
        else:
            leader = self.home_team.name if self.home_score > self.away_score else self.away_team.name
            lead_status = f"{leader} leads by {score_diff}"
        is_overtime = self.current_period > self.rules.number_of_periods
        is_last_period = self.current_period >= self.rules.number_of_periods
        # indicates if we are during the first half of total time to play
        is_first_half = self.current_period <= (self.rules.number_of_periods / 2)
        # specific indicator to the last 30 seconds of a game part
        end_of_period = (self.minutes_remaining == 0 and self.seconds_remaining <= 30)
        # indicator to the end of a tight game. will be used to-
        is_clutch_time = (is_last_period and self.minutes_remaining < 2 and score_diff < 6)
        # another indicator that will be used to indicate when the possession matters
        is_late_close_game = (is_last_period and self.minutes_remaining < 4 and score_diff < 10)
        completed_periods = self.current_period - 1
        reg_periods_completed = min(completed_periods, self.rules.number_of_periods)
        ot_periods_completed = max(0, completed_periods - self.rules.number_of_periods)
        elapsed_minutes = (reg_periods_completed * self.rules.period_length_minutes) + \
                          (ot_periods_completed * self.rules.overtime_length_minutes)
        current_period_max = self.rules.overtime_length_minutes if is_overtime else self.rules.period_length_minutes
        elapsed_minutes += (current_period_max - self.minutes_remaining - (self.seconds_remaining / 60))
        summary.append("[GAME CONTEXT]")
        summary.append(
            f"Score: {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name} ({lead_status})")
        summary.append(
            f"Time: Period {self.current_period}, {self.minutes_remaining}:{self.seconds_remaining:02d} left")
        summary.append(f"Coach Timeouts left: {my_team.timeouts_remaining}")
        summary.append(f"Upcoming Schedule Density: {my_team.upcoming_schedule_density}")
        # possession matters during clutch time
        if end_of_period or is_clutch_time:
            summary.append(f"Possession: {self.possession}")
        # during the last period when the difference is small the venue matters to decision making
        if is_last_period and score_diff < 10:
            summary.append(f"Venue: {self.venue_type} (Coaching {self.target_team})")
        summary.append("\n[MOMENTUM & STRATEGY]")
        summary.append(f"Trend: {self.momentum.overall_trend}")
        # crowd affects the game especially during the last period when the difference is small
        if is_last_period and score_diff < 10:
            summary.append(f"Crowd Intensity: {self.momentum.crowd_intensity}")

        summary.append(f"Caoch Directives: {self.directives.primary_strategy} | Defensive Focus: {self.directives.defensive_focus}")


        summary.append("\n[ON COURT PERSONNEL]")
        for p in my_team.active_lineup:
            age_info = f", Age: {p.age}" if is_late_close_game else ""
            summary.append(f"- {fmt_p(p)} (EFF: {p.efficiency_score}, Fatigue: {p.fatigue_level}{age_info})")


        if opp_team.active_lineup:
            top_threat = max(opp_team.active_lineup, key=lambda p: p.efficiency_score)
            summary.append(f"\n[OPPONENT THREAT ON COURT]")
            summary.append(
                f"- {fmt_p(top_threat)} (EFF: {top_threat.efficiency_score}, Fouls: {top_threat.current_fouls})")


        alarms = []
        unavailable_players = [fmt_p(p) for p in my_team.players if
                               p.fatigue_level == "Injured" or p.current_fouls >= self.rules.max_fouls_per_player]
        if unavailable_players:
            alarms.append(f"UNAVAILABLE (Injured/Fouled Out): {', '.join(unavailable_players)}")


        exhausted = [fmt_p(p) for p in my_team.active_lineup if p.fatigue_level in ["Tired", "Exhausted"]]
        if exhausted:
            alarms.append(f"CRITICAL FATIGUE: {', '.join(exhausted)} need rest!")


        foul_threshold_diff = 3 if is_first_half else 1
        foul_threshold = self.rules.max_fouls_per_player - foul_threshold_diff
        foul_trouble = [f"{fmt_p(p)} ({p.current_fouls}/{self.rules.max_fouls_per_player} fouls)" for p in my_team.players
                        if p.current_fouls >= foul_threshold and p.current_fouls < self.rules.max_fouls_per_player]
        if foul_trouble:
            alarms.append(f"FOUL TROUBLE RISK: {', '.join(foul_trouble)}")


        if opp_team.team_fouls >= self.rules.team_fouls_to_penalty:
            alarms.append("TACTICAL ADVANTAGE: Opponent is in the PENALTY. We shoot free throws on every foul!")
        if my_team.team_fouls >= self.rules.team_fouls_to_penalty:
            alarms.append("DANGER: We are in the PENALTY. Defend without fouling!")


        if is_clutch_time and my_team.timeouts_remaining == 0:
            alarms.append("CRITICAL: 0 timeouts remaining in clutch time!")

        if alarms:
            summary.append("\n[ACTIONABLE ALERTS]")
            for alarm in alarms:
                summary.append(f"- {alarm}")

        # if the coach wants to develop young players we will send the ones who played less than 30 percents of the game
        if getattr(self.directives, 'game_objective', '') == "Develop Young Players" and elapsed_minutes > 0:
            young_bench = [
                fmt_p(p) for p in my_team.players
                if not p.is_on_court
                   and p.age < 25
                   and p.minutes_played < (0.3 * elapsed_minutes)
                   and p.fatigue_level != "Injured"
            ]
            if young_bench:
                summary.append("\n[DEVELOPMENT OPPORTUNITY]")
                summary.append(f"Consider subbing in young players (played <30% of game): {', '.join(young_bench)}")

        return "\n".join(summary)

    model_config = ConfigDict(
        json_schema_extra={"example": GAME_STATE_EXAMPLE}
    )