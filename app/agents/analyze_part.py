from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport
from app.agents.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.core.config import get_settings


class AnalystAgent:
    def __init__(self):
        settings = get_settings()
        # We define the temperature to be 0 so the model will be deterministic with fewer hallucinations
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0,
            api_key=settings.openai_api_key
        ).with_structured_output(AnalysisReport)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT_TEMPLATE)
        ])

    async def analyze(self, state: GameState) -> AnalysisReport:
        """
        The process of getting a summary of the game state and finally
        receiving an analysis report from the AI
        """
        try:
            game_summary_text = state.to_ai_summary()
            chain = self.prompt_template | self.llm
            report = await chain.ainvoke({"game_summary_text": game_summary_text})
            return report

        except Exception as e:
            print(f"Error during agent execution: {str(e)}")
            raise e