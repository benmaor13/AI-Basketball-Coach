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
    # where the game is played
    venue_type: Literal["Home", "Away", "Neutral"] = Field(
        ...,
        description="Indicates the game location. 'Home' means playing at the home_team's arena."
    )
    # which team is the one of the coach
    target_team: Literal["Home", "Away"] = Field(
        default="Home",
        description="The team the AI is currently coaching."
    )
    # simple stats about the current situation in the game
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

    # validating some parameters according to league rules
    @model_validator(mode='after')
    def validate_game_logic(self) -> 'GameState':
        if self.home_timeouts_remaining > self.rules.max_timeouts or \
                self.away_timeouts_remaining > self.rules.max_timeouts:
            raise ValueError(f"A team cannot have more than {self.rules.max_timeouts} timeouts.")

        is_overtime = self.current_period > self.rules.number_of_periods
        max_minutes_for_period = self.rules.overtime_length_minutes if is_overtime else self.rules.period_length_minutes

        if self.minutes_remaining > max_minutes_for_period:
            raise ValueError(
                f"Invalid time: Minutes remaining ({self.minutes_remaining}) cannot exceed "
                f"the maximum length for period {self.current_period} ({max_minutes_for_period} mins)."
            )

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

    def to_ai_summary(self) -> str:
        """
        Generates the message to the AI that will be short as possible,
        accurate with the most relevant info and is written (as much as possible)
        in a specific pattern. the design makes the AI more accurate and also
        makes hallucinating less common
        """

        # parameters which indicate abbout the current situation in the game, and used for further calculations.
        score_diff = abs(self.home_score - self.away_score)
        is_last_period = self.current_period >= self.rules.number_of_periods
        is_first_half = self.current_period <= (self.rules.number_of_periods / 2)
        is_clutch_time = (is_last_period and self.minutes_remaining < 2 and score_diff < 6)
        is_late_close_game = (is_last_period and self.minutes_remaining < 4 and score_diff < 10)
        end_of_period = (self.minutes_remaining == 0 and self.seconds_remaining <= 30)

        # coach directives, that impact the AI decisions
        off_strat = self.directives.offensive_strategy
        def_focus = self.directives.defensive_focus
        objective = self.directives.game_objective

        # gathering the relevant information about the players
        def fmt_p(p) -> str:
            rank_label = f"Rank :{p.position_rank}"
            stats = [f"EFF: {p.efficiency_score}", f"Style: {p.style}"]

            # the ft percentage is relevant(in addition to the calculation of efficiency) to specific directives
            if "Kill the Clock" in objective or "Paint" in off_strat or is_clutch_time:
                stats.append(f"FT: {p.season_ft_pct}%")

            # Cooldown logic to prevent rapid 'yo-yo' substitutions
            if p.is_on_court and getattr(p, 'current_stint_minutes',
                                         0.0) < 2.0 and p.fatigue_level != "Injured" and p.current_fouls < (
                    self.rules.max_fouls_per_player - 1):
                stats.append("JUST SUBBED IN (Do Not Sub Out)")

            stats_str = ", ".join(stats)
            # age is relevant when it is the end of a tight game or when coach wants to develop young players
            age_info = f", Age: {p.age}" if is_late_close_game or "Develop Youth" in objective else ""

            return f"{p.name} (#{p.number}, {p.position}, {rank_label}{age_info}) [{stats_str}, Fouls: {p.current_fouls}, Fatigue: {p.fatigue_level}]"

        # gathers the information used to make the summary
        summary = []
        # the coach's team and the other team
        my_team = self.home_team if self.target_team == "Home" else self.away_team
        opp_team = self.away_team if self.target_team == "Home" else self.home_team

        if self.home_score == self.away_score:
            lead_status = "Game is TIED"
        else:
            leader = self.home_team.name if self.home_score > self.away_score else self.away_team.name
            lead_status = f"{leader} leads by {score_diff}"
        # creating the main context to the AI
        summary.append("[GAME CONTEXT]")

        # Explicit Semantic Trigger for the AI regarding Game Phase
        game_phase = "CLUTCH TIME" if is_clutch_time else "Late Close Game" if is_late_close_game else "Regular Flow"
        summary.append(f"Game Phase: {game_phase}")

        # score
        summary.append(
            f"Score: {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name} ({lead_status})")
        # time
        summary.append(
            f"Time: Period {self.current_period}, {self.minutes_remaining}:{self.seconds_remaining:02d} left")

        # wins\losses streak in a known sports format (to better understanding of the AI)
        def fmt_streak(s):
            return f"{s}W" if s > 0 else f"{abs(s)}L" if s < 0 else "0"

        # these lines improve the context of the game in general
        summary.append(
            f"Matchup: {self.home_team.name} (Rank #{self.home_team.league_position}) vs. {self.away_team.name} (Rank #{self.away_team.league_position})")
        summary.append(
            f"Our Stats ({my_team.name}): Off Rank #{my_team.offensive_rank}, Def Rank #{my_team.defensive_rank}, Streak: {fmt_streak(my_team.win_streak)}")
        summary.append(
            f"Opp Stats ({opp_team.name}): Off Rank #{opp_team.offensive_rank}, Def Rank #{opp_team.defensive_rank}, Streak: {fmt_streak(opp_team.win_streak)}")

        summary.append(f"Timeouts Left: {my_team.timeouts_remaining} / {self.rules.max_timeouts}")
        summary.append(
            f"Team Fouls (Penalty at {self.rules.team_fouls_to_penalty}): Us: {my_team.team_fouls}, Opponent: {opp_team.team_fouls}")
        # the possession is relevant only in specific circumstances
        if end_of_period or is_clutch_time:
            summary.append(f"Possession: {self.possession}")
        # adding info about the coach directives
        summary.append("\n[STRATEGIC CONTEXT]")
        summary.append(f"Objective: {objective} |MY Risk Tolerance: {self.directives.risk_tolerance}")
        summary.append(f"Scheme: Offense='{off_strat}', Defense='{def_focus}'")
        summary.append(f"Momentum Trend: {self.momentum.overall_trend}")
        # atmosphere is especially relevant in the end of a tight game
        if is_last_period and score_diff < 10:
            summary.append(f"Venue: {self.venue_type} | Crowd Intensity: {self.momentum.crowd_intensity}")
        summary.append("\n[ON COURT PERSONNEL]")
        for p in my_team.active_lineup:
            summary.append(f"- {fmt_p(p)}")
        # we do not add player who are injured or exceeded the foul limit
        available_bench = [p for p in my_team.players if
                           not p.is_on_court and p.fatigue_level != "Injured" and p.current_fouls < self.rules.max_fouls_per_player]

        # Sorting bench to prevent LLM Position Bias
        available_bench_sorted = sorted(available_bench, key=lambda p: (p.position_rank, -p.efficiency_score))
        if available_bench_sorted:
            summary.append("\n[AVAILABLE BENCH PERSONNEL]")
            for p in available_bench_sorted:
                summary.append(f"- {fmt_p(p)}")

        # making sure the AI knows why certain players are missing from the bench options
        unavailable_players = [p for p in my_team.players if
                               not p.is_on_court and (
                                       p.fatigue_level == "Injured" or p.current_fouls >= self.rules.max_fouls_per_player)]
        if unavailable_players:
            summary.append("\n[UNAVAILABLE PERSONNEL (DO NOT SUB IN)]")
            for p in unavailable_players:
                reason = "Injured" if p.fatigue_level == "Injured" else "Fouled Out"
                summary.append(f"- {p.name} (#{p.number}) [Status: {reason}]")

        # the "most dangerous" player of the other team based on efficiency and position rank
        if opp_team.active_lineup:
            top_threat = max(opp_team.active_lineup, key=lambda p: (p.efficiency_score, -p.position_rank))
            summary.append(f"\n[OPPONENT THREAT ON COURT]")
            summary.append(f"- {fmt_p(top_threat)}")
        # important messages to the AI based on the current situation
        alarms = []
        # players in the other team that have foul trouble
        opp_foul_trouble = [f"{p.name} (#{p.number}) ({p.current_fouls} fouls)" for p in opp_team.active_lineup
                            if p.current_fouls >= (self.rules.max_fouls_per_player - 2)]
        if opp_foul_trouble:
            alarms.append(
                f"[Consider Foul Strategy] OPPONENT VULNERABILITY: Attack {', '.join(opp_foul_trouble)} to force disqualification!")

        # injured players still on the court must be subbed out immediately
        injured_on_court = [f"{p.name} (#{p.number})" for p in my_team.active_lineup if p.fatigue_level == "Injured"]
        if injured_on_court:
            alarms.append(
                f"[Requires Substitution] MANDATORY SUB: {', '.join(injured_on_court)} are INJURED and must be subbed out immediately!")
        # noticeable alert when the best player on the court is tired
        for p in my_team.active_lineup:
            if p.position_rank == 1:
                if p.current_fouls >= (self.rules.max_fouls_per_player - 1):
                    alarms.append(
                        f"[Risk Warning] STAR IN FOUL TROUBLE: {p.name} (#{p.number}) has {p.current_fouls} fouls!")
                if p.fatigue_level in ["Tired", "Exhausted"]:
                    alarms.append(f"[Risk Warning] STAR FATIGUE: {p.name} (#{p.number}) is {p.fatigue_level}.")
        # list of the tired players on the court
        exhausted = [f"{p.name} (#{p.number})" for p in my_team.active_lineup if
                     p.fatigue_level in ["Tired", "Exhausted"] and p.position_rank > 1]
        if exhausted:
            alarms.append(f"[Requires Substitution] FATIGUE: {', '.join(exhausted)} are tired.")
        # players who have "foul trouble", while taking into account current part of the game
        foul_threshold_diff = 3 if is_first_half else 1
        foul_threshold = self.rules.max_fouls_per_player - foul_threshold_diff
        foul_trouble = [f"{p.name} (#{p.number}) ({p.current_fouls})" for p in my_team.active_lineup
                        if p.current_fouls >= foul_threshold and p.position_rank > 1]
        if foul_trouble:
            alarms.append(f"[Requires Substitution] FOUL TROUBLE: {', '.join(foul_trouble)}")
        # alert when the other team exceeded the foul limit
        if opp_team.team_fouls >= self.rules.team_fouls_to_penalty:
            alarms.append(
                "[Offensive Focus Shift] TACTICAL ADVANTAGE: Opponent in PENALTY. Attack the paint to draw fouls!")
        # alert when out team exceeded the foul limit
        if my_team.team_fouls >= self.rules.team_fouls_to_penalty:
            alarms.append("[Defensive Scheme Adjustment] DANGER: We are in the PENALTY. Play clean defense!")
        # using the last timeout smartly and also avoiding a technical foul by calling timeout when 0 remaining
        if my_team.timeouts_remaining == 1:
            alarms.append("[Timeout Warning] CRITICAL: 1 timeouts left! Use carefully.")
        if my_team.timeouts_remaining == 0:
            alarms.append("[Timeout Warning] CRITICAL: 0 timeouts left! Do Not Call timeout anymore!.")
        if alarms:
            summary.append("\n[ACTIONABLE ALERTS]")
            for alarm in alarms:
                summary.append(f"- {alarm}")
        # the young age matters when the coach wants to develop young players
        if "Develop Youth" in objective:
            young_bench = [f"{p.name} (#{p.number})" for p in available_bench_sorted if p.age < 25]
            if young_bench:
                summary.append("\n[DEVELOPMENT OPPORTUNITY]")
                summary.append(
                    f"[Requires Substitution] Mandatory priority: Sub in these U25 players: {', '.join(young_bench)}")

        return "\n".join(summary)

    model_config = ConfigDict(
        json_schema_extra={"example": GAME_STATE_EXAMPLE}
    )