from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.core.constants import *
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

    # where the game is played
    venue_type: Literal["Home", "Away", "Neutral"] = Field(
        ...,
        description="Indicates the game location. 'Home' means playing at the home_team's arena."
    )
    # which team the AI is coaching
    target_team: Literal["Home", "Away"] = Field(
        default="Home",
        description="The team the AI is currently coaching."
    )
    # score
    home_score: int = Field(..., ge=0, description="Total points scored by the home team.")
    away_score: int = Field(..., ge=0, description="Total points scored by the away team.")
    # clock
    current_period: int = Field(..., ge=1, description="Current game period. e.g., 1-4 for quarters.")
    minutes_remaining: int = Field(..., ge=0, le=20, description="Minutes left on the clock.")
    seconds_remaining: int = Field(..., ge=0, le=59, description="Seconds left on the clock.")
    # possession
    possession: Literal["Home", "Away", "Neutral"] = Field(default="Neutral")

    # live bilateral stats — single source of truth (not duplicated on Team)
    home_timeouts_remaining: int = Field(default=3, ge=0)
    away_timeouts_remaining: int = Field(default=3, ge=0)
    home_team_fouls: int = Field(default=0, ge=0)
    away_team_fouls: int = Field(default=0, ge=0)
    # validation
    @model_validator(mode='after')
    def validate_game_logic(self) -> 'GameState':
        # timeouts cannot exceed league maximum
        if self.home_timeouts_remaining > self.rules.max_timeouts or \
                self.away_timeouts_remaining > self.rules.max_timeouts:
            raise ValueError(f"A team cannot have more than {self.rules.max_timeouts} timeouts.")

        # minutes remaining cannot exceed the period length
        is_overtime = self.current_period > self.rules.number_of_periods
        max_minutes_for_period = (
            self.rules.overtime_length_minutes if is_overtime
            else self.rules.period_length_minutes
        )
        if self.minutes_remaining > max_minutes_for_period:
            raise ValueError(
                f"Invalid time: Minutes remaining ({self.minutes_remaining}) cannot exceed "
                f"the maximum length for period {self.current_period} ({max_minutes_for_period} mins)."
            )
        # player foul validation against league rules
        max_fouls = self.rules.max_fouls_per_player
        for team in [self.home_team, self.away_team]:
            for player in team.players:
                if player.current_fouls > max_fouls:
                    raise ValueError(
                        f"Data Error: Player '{player.name}' ({team.name}) has {player.current_fouls} fouls, "
                        f"which exceeds the absolute league limit of {max_fouls}."
                    )
                if player.is_on_court and player.current_fouls >= max_fouls:
                    raise ValueError(
                        f"Game Logic Error: Player '{player.name}' is on court but has already "
                        f"fouled out ({player.current_fouls}/{max_fouls} fouls)."
                    )

        return self
    # Fields that are used in the summary
    def _get_my_timeouts(self) -> int:
        """Returns the coaching team's remaining timeouts"""
        return self.home_timeouts_remaining if self.target_team == "Home" else self.away_timeouts_remaining

    def _get_my_fouls(self) -> int:
        """Returns the coaching team's current period fouls"""
        return self.home_team_fouls if self.target_team == "Home" else self.away_team_fouls

    def _get_opp_fouls(self) -> int:
        """Returns the opponent team's current period fouls"""
        return self.away_team_fouls if self.target_team == "Home" else self.home_team_fouls

    def _compute_game_flags(self) -> dict:
        """
        Computes all boolean game-state flags used across multiple sections.
        """
        score_diff = abs(self.home_score - self.away_score)
        is_last_period = self.current_period >= self.rules.number_of_periods
        is_first_half = self.current_period <= (self.rules.number_of_periods / 2)
        is_clutch_time = is_last_period and self.minutes_remaining < CLUTCH_TIME_MINUTES and score_diff < CLUTCH_TIME_MAX_SCORE_DIFF
        is_late_close_game = is_last_period and self.minutes_remaining < LATE_GAME_MINUTES and score_diff < LATE_GAME_MAX_SCORE_DIFF
        end_of_period = self.minutes_remaining == 0 and self.seconds_remaining <= 30

        return {
            "score_diff": score_diff,
            "is_last_period": is_last_period,
            "is_first_half": is_first_half,
            "is_clutch_time": is_clutch_time,
            "is_late_close_game": is_late_close_game,
            "end_of_period": end_of_period,
        }

    def _fmt_streak(self, s: int) -> str:
        """Formats win/loss streak in standard sports notation"""
        return f"{s}W" if s > 0 else f"{abs(s)}L" if s < 0 else "0"

    def _fmt_player(self, p, flags: dict) -> str:
        """
        Formats a single player's info for the AI prompt.
        """
        # Rank in the position and data about efficiency and playStyle
        rank_label = f"Rank:{p.position_rank}"
        stats = [f"EFF:{p.efficiency_score}", f"Style:{p.style}"]

        # FT% is only relevant in specific strategic contexts, keeps prompt shorter otherwise
        show_ft = (
            self.directives.game_objective == "Kill the Clock"
            or self.directives.offensive_strategy == "Attack the Paint"
            or flags["is_clutch_time"]
        )
        # if it is relevant we add this stat
        if show_ft:
            stats.append(f"FT:{p.season_ft_pct}%")
        # Cooldown flag — prevents rapid yo-yo substitutions
        just_subbed_in = (
            p.is_on_court
            and p.current_stint_minutes < MIN_STINT_MINUTES
            and p.fatigue_level != "Injured"
            and p.current_fouls < (self.rules.max_fouls_per_player - 1)
        )
        if just_subbed_in:
            stats.append("JUST SUBBED IN (Do Not Sub Out)")
        stats_str = ", ".join(stats)
        # Age only shown when relevant to the decision (late tight game or youth development)
        show_age = flags["is_late_close_game"] or self.directives.game_objective == "Develop Youth"
        age_info = f", Age:{p.age}" if show_age else ""
        return (
            f"{p.name} (#{p.number}, {p.position}, {rank_label}{age_info})"
            f" [{stats_str}, Fouls:{p.current_fouls}, Fatigue:{p.fatigue_level}]"
        )

    def _build_game_context(self, my_team, opp_team, flags: dict) -> list[str]:
        """Builds the [GAME CONTEXT] section — score, time, matchup, fouls, timeouts."""
        lines = []
        score_diff = flags["score_diff"]

        if self.home_score == self.away_score:
            lead_status = "Game is TIED"
        else:
            leader = self.home_team.name if self.home_score > self.away_score else self.away_team.name
            lead_status = f"{leader} leads by {score_diff}"

        game_phase = (
            "CLUTCH TIME" if flags["is_clutch_time"]
            else "Late Close Game" if flags["is_late_close_game"]
            else "Regular Flow"
        )

        lines.append("[GAME CONTEXT]")
        # Explicit semantic trigger for the AI — game phase affects its entire reasoning
        lines.append(f"Game Phase: {game_phase}")
        lines.append(
            f"Score: {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name} ({lead_status})"
        )
        lines.append(
            f"Time: Period {self.current_period}, {self.minutes_remaining}:{self.seconds_remaining:02d} left"
        )
        lines.append(
            f"Matchup: {self.home_team.name} (Rank #{self.home_team.league_position})"
            f" vs. {self.away_team.name} (Rank #{self.away_team.league_position})"
        )
        lines.append(
            f"Our Stats ({my_team.name}): Off Rank #{my_team.offensive_rank},"
            f" Def Rank #{my_team.defensive_rank}, Streak: {self._fmt_streak(my_team.win_streak)}"
        )
        lines.append(
            f"Opp Stats ({opp_team.name}): Off Rank #{opp_team.offensive_rank},"
            f" Def Rank #{opp_team.defensive_rank}, Streak: {self._fmt_streak(opp_team.win_streak)}"
        )
        # Timeouts
        lines.append(f"Timeouts Left: {self._get_my_timeouts()} / {self.rules.max_timeouts}")

        # Fouls
        lines.append(
            f"Team Fouls (Penalty at {self.rules.team_fouls_to_penalty}):"
            f" Us: {self._get_my_fouls()}, Opponent: {self._get_opp_fouls()}"
        )

        # Possession is only tactically relevant at end of period or clutch time
        if flags["end_of_period"] or flags["is_clutch_time"]:
            lines.append(f"Possession: {self.possession}")

        return lines

    def _build_strategic_context(self, my_team, opp_team, flags: dict) -> list[str]:
        """Builds the [STRATEGIC CONTEXT] section"""
        lines = []
        lines.append("\n[STRATEGIC CONTEXT]")
        lines.append(
            f"Objective: {self.directives.game_objective} | Risk Tolerance: {self.directives.risk_tolerance}"
        )
        lines.append(
            f"Scheme: Offense='{self.directives.offensive_strategy}',"
            f" Defense='{self.directives.defensive_focus}'"
        )
        lines.append(f"Momentum Trend: {self.momentum.overall_trend}")

        # Crowd atmosphere only meaningful in tight late-game situations
        if flags["is_last_period"] and flags["score_diff"] < LATE_GAME_MAX_SCORE_DIFF:
            lines.append(f"Venue: {self.venue_type} | Crowd Intensity: {self.momentum.crowd_intensity}")

        return lines

    def _build_personnel(self, my_team, flags: dict) -> list[str]:
        """
        Builds the personnel sections:
        - ON COURT (active lineup)
        - AVAILABLE BENCH (sorted to prevent LLM position bias)
        - UNAVAILABLE (injured or fouled out—so AI knows why they're missing)
        """
        lines = []
        lines.append("\n[ON COURT PERSONNEL]")
        for p in my_team.active_lineup:
            lines.append(f"- {self._fmt_player(p, flags)}")

        # Exclude injured and fouled-out players from bench options
        available_bench = [
            p for p in my_team.players
            if not p.is_on_court
            and p.fatigue_level != "Injured"
            and p.current_fouls < self.rules.max_fouls_per_player
        ]
        # Sort by position rank then efficiency to prevent LLM recency bias (minus to make the opposite order)
        available_bench_sorted = sorted(available_bench, key=lambda p: (p.position_rank, -p.efficiency_score))

        if available_bench_sorted:
            lines.append("\n[AVAILABLE BENCH PERSONNEL]")
            for p in available_bench_sorted:
                lines.append(f"- {self._fmt_player(p, flags)}")

        # Explicitly list unavailable players so the AI doesn't hallucinate subbing them in
        unavailable = [
            p for p in my_team.players
            if not p.is_on_court
            and (p.fatigue_level == "Injured" or p.current_fouls >= self.rules.max_fouls_per_player)
        ]
        if unavailable:
            lines.append("\n[UNAVAILABLE PERSONNEL (DO NOT SUB IN)]")
            for p in unavailable:
                reason = "Injured" if p.fatigue_level == "Injured" else "Fouled Out"
                lines.append(f"- {p.name} (#{p.number}) [Status: {reason}]")

        return lines

    def _build_opponent_threat(self, opp_team, flags: dict) -> list[str]:
        """Identifies and formats the most dangerous opponent on the court."""
        lines = []
        if opp_team.active_lineup:
            top_threat = max(opp_team.active_lineup, key=lambda p: (p.efficiency_score, -p.position_rank))
            lines.append("\n[OPPONENT THREAT ON COURT]")
            lines.append(f"- {self._fmt_player(top_threat, flags)}")
        return lines

    def _build_alarms(self, my_team, opp_team, available_bench_sorted, flags: dict) -> list[str]:
        """
        Builds the [ACTIONABLE ALERTS] section.
        Alarms are prioritized, labeled instructions that directly
        map to action_types in the AI's structured output.
        """
        alarms = []

        # Opponent's vulnerability
        opp_foul_trouble = [
            f"{p.name} (#{p.number}) ({p.current_fouls} fouls)"
            for p in opp_team.active_lineup
            if p.current_fouls >= (self.rules.max_fouls_per_player - OPPONENT_FOUL_TROUBLE_BUFFER)
        ]
        if opp_foul_trouble:
            alarms.append(
                f"[Consider Foul Strategy] OPPONENT VULNERABILITY:"
                f" Attack {', '.join(opp_foul_trouble)} to force disqualification!"
            )

        # mandatory substitutions
        injured_on_court = [
            f"{p.name} (#{p.number})"
            for p in my_team.active_lineup
            if p.fatigue_level == "Injured"
        ]
        if injured_on_court:
            alarms.append(
                f"[Requires Substitution] MANDATORY SUB:"
                f" {', '.join(injured_on_court)} are INJURED and must be subbed out immediately!"
            )

        # Star Player warning
        for p in my_team.active_lineup:
            if p.position_rank == 1:
                if p.current_fouls >= (self.rules.max_fouls_per_player - STAR_PLAYER_FOUL_TROUBLE_BUFFER):
                    alarms.append(
                        f"[Risk Warning] STAR IN FOUL TROUBLE:"
                        f" {p.name} (#{p.number}) has {p.current_fouls} fouls!"
                    )
                if p.fatigue_level in ("Tired", "Exhausted"):
                    alarms.append(
                        f"[Risk Warning] STAR FATIGUE: {p.name} (#{p.number}) is {p.fatigue_level}."
                    )

        # Nonstar fatigue warning
        exhausted = [
            f"{p.name} (#{p.number})"
            for p in my_team.active_lineup
            if p.fatigue_level in ("Tired", "Exhausted") and p.position_rank > 1
        ]
        if exhausted:
            alarms.append(f"[Requires Substitution] FATIGUE: {', '.join(exhausted)} are tired.")

        # foul trouble
        foul_threshold_diff = FOUL_TROUBLE_BUFFER_FIRST_HALF if flags["is_first_half"] else FOUL_TROUBLE_BUFFER_SECOND_HALF
        foul_threshold = self.rules.max_fouls_per_player - foul_threshold_diff
        foul_trouble = [
            f"{p.name} (#{p.number}) ({p.current_fouls})"
            for p in my_team.active_lineup
            if p.current_fouls >= foul_threshold and p.position_rank > 1
        ]
        if foul_trouble:
            alarms.append(f"[Requires Substitution] FOUL TROUBLE: {', '.join(foul_trouble)}")

        # penalty situation
        if self._get_opp_fouls() >= self.rules.team_fouls_to_penalty:
            alarms.append(
                "[Offensive Focus Shift] TACTICAL ADVANTAGE:"
                " Opponent in PENALTY. Attack the paint to draw fouls!"
            )
        if self._get_my_fouls() >= self.rules.team_fouls_to_penalty:
            alarms.append(
                "[Defensive Scheme Adjustment] DANGER: We are in the PENALTY. Play clean defense!"
            )

        # timeout warnings
        my_timeouts = self._get_my_timeouts()
        if my_timeouts == 1:
            alarms.append("[Timeout Warning] CRITICAL: 1 timeout left! Use carefully.")
        if my_timeouts == 0:
            alarms.append("[Timeout Warning] CRITICAL: 0 timeouts left! Do NOT call timeout.")

       # Optional Youth develompent
        if self.directives.game_objective == "Develop Youth":
            young_bench = [
                f"{p.name} (#{p.number})"
                for p in available_bench_sorted
                if p.age < YOUTH_AGE_THRESHOLD
            ]
            if young_bench:
                alarms.append(
                    f"[Requires Substitution] DEVELOPMENT PRIORITY:"
                    f" Sub in U25 players: {', '.join(young_bench)}"
                )

        return alarms

    def to_ai_summary(self) -> str:
        """
        Generates the prompt body sent to the AI.
        Designed to be as short as possible while remaining accurate —
        structured sections and explicit semantic labels reduce hallucination.
        """
        flags = self._compute_game_flags()
        my_team = self.home_team if self.target_team == "Home" else self.away_team
        opp_team = self.away_team if self.target_team == "Home" else self.home_team
        summary = []
        summary += self._build_game_context(my_team, opp_team, flags)
        summary += self._build_strategic_context(my_team, opp_team, flags)
        personnel_lines, available_bench_sorted = self._build_personnel(my_team, flags)
        summary += personnel_lines
        summary += self._build_opponent_threat(opp_team, flags)
        alarms = self._build_alarms(my_team, opp_team, available_bench_sorted, flags)
        if alarms:
            summary.append("\n[ACTIONABLE ALERTS]")
            for alarm in alarms:
                summary.append(f"- {alarm}")

        return "\n".join(summary)

    model_config = ConfigDict(
        json_schema_extra={"example": GAME_STATE_EXAMPLE}
    )