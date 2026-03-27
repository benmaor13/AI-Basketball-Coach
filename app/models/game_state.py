from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport, TacticalAction
from app.agents.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class AnalystAgent:
    """
    The intelligence layer of HoopsAI.
    Converts raw game data into high-level tactical recommendations.
    """

    def __init__(self):
        # Targeting gpt-4o for its superior reasoning in multi-variable scenarios
        self.model_name = "gpt-4o"

    async def analyze(self, state: GameState) -> AnalysisReport:
        """
        Primary analysis pipeline.
        Validates the state, prepares AI context, and returns structured insights.
        """
        try:
            #Serialize the state for AI consumption.
            # This prepares the data to the LLM in a structured way.
            game_data_json = state.model_dump_json(indent=2)
            # Return a context-aware Mock report for current development phase
            report = self._get_mock_report()
            return report

        except Exception as e:
            print(f"Error during agent execution: {str(e)}")
            raise e

    def _get_mock_report(self) -> AnalysisReport:
        """
        Generates a realistic coaching report aligned with defined Literal action types:
        ['Substitution', 'Timeout', 'Defensive Shift', 'Pace Adjustment']
        """
        return AnalysisReport(
            summary="Opponent is capitalizing on our interior foul trouble and high fatigue in the backcourt.",
            main_threat="Opponent's Power Forward is dominating the paint. Our transition defense is compromised.",
            recommended_actions=[
                TacticalAction(
                    action_type="Substitution",
                    description="Replace starting Center (4 fouls, 'Tired') with backup (Position Rank 2) to preserve the starter for the final 5 minutes.",
                    priority="High",
                    expected_impact="Protects the rim without risking a disqualification (foul-out) of our primary defender."
                ),
                TacticalAction(
                    action_type="Defensive Shift",
                    description="Switch from Man-to-Man to a '2-3 Zone' to pack the paint and limit opponent's high-percentage layups.",
                    priority="High",
                    expected_impact="Forces the opponent to take contested perimeter shots instead of easy interior points."
                ),
                TacticalAction(
                    action_type="Pace Adjustment",
                    description="Slow down the game. Avoid early-clock shots and focus on half-court execution to let 'Exhausted' players recover.",
                    priority="Medium",
                    expected_impact="Reduces the overall game tempo, limiting opponent's fast-break opportunities."
                ),
                TacticalAction(
                    action_type="Timeout",
                    description="Call a 60-second timeout now to implement the defensive shift and disrupt the opponent's 10-2 scoring run.",
                    priority="Medium",
                    expected_impact="Resets team focus and stops the 'bleeding' before the lead evaporates."
                )
            ],
            risk_assessment="High risk of losing the rebounding battle if the 'Small Ball' lineup stays on court for more than 3 minutes.",
            confidence_score=0.96
        )