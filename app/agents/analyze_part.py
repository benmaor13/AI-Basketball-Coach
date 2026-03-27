from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport, TacticalAction
from app.agents.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class AnalystAgent:
    """
    Acts as the 'Brain' of the system.
    It processes raw basketball data and translates it into actionable coaching insights.
    """

    def __init__(self):
        # Using gpt-4o for high-level tactical reasoning
        self.model_name = "gpt-4o"

    async def analyze(self, state: GameState) -> AnalysisReport:
        """
        Processes a GameState and returns a tactical AnalysisReport.
        """
        try:
            # Step 1: Serialize the incoming Pydantic model
            game_data_json = state.model_dump_json(indent=2)

            # TODO: Future Step - Connect to OpenAI using 'game_data_json'

            # Step 2: Return a professional mock response for pipeline validation
            report = self._get_mock_report()

            return report

        except Exception as e:
            print(f"Error during agent execution: {str(e)}")
            raise e

    def _get_mock_report(self) -> AnalysisReport:
        """
        Mock report adjusted to match the required Literal action types:
        ["Substitution", "Timeout", "Defensive Shift", "Pace Adjustment"]
        """
        return AnalysisReport(
            summary="Opponent is exploiting the high-pick-and-roll. Our defensive rotation is consistently late on the weak side.",
            main_threat="High perimeter vulnerability. Opponent's SG is finding open lanes due to our low fatigue management.",
            recommended_actions=[
                TacticalAction(
                    action_type="Substitution",
                    description="Replace starting PF (Fatigue: Tired) with Bench PF (Position Rank 2) to improve lateral quickness.",
                    priority="High",
                    expected_impact="Improved rim protection and better recovery on defensive rotations."
                ),
                TacticalAction(
                    action_type="Defensive Shift",
                    description="Switch from Man-to-Man to a 2-3 Zone defense to clog the paint and force outside shots.",
                    priority="High",
                    expected_impact="Neutralize the opponent's interior scoring and force low-percentage contested 3s."
                ),
                TacticalAction(
                    action_type="Timeout",
                    description="Call a 30-second timeout to break the opponent's 8-0 scoring run and reset offensive sets.",
                    priority="Medium",
                    expected_impact="Disrupt opponent momentum and provide rest for the core lineup."
                ),
                TacticalAction(
                    action_type="Pace Adjustment",
                    description="Slow down the transition game. Utilize the full 24-second clock to limit opponent possessions.",
                    priority="Medium",
                    expected_impact="Lower the overall game intensity to match our current fatigue levels and stabilize the lead."
                )
            ],
            risk_assessment="High risk of losing the lead in the 4th quarter if defensive intensity isn't restored via substitutions.",
            confidence_score=0.98
        )