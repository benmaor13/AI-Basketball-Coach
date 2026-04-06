from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import RateLimitError, APITimeoutError, APIConnectionError, AuthenticationError

from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport
from app.agents.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_prompt_variables
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalystAgent:
    def __init__(self):
        settings = get_settings()

        # Exposed so main.py health check can report which model is active
        self.model_name = settings.model_name

        # Temperature=0 — deterministic output, reduces hallucinations
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0,
            api_key=settings.openai_api_key
        ).with_structured_output(AnalysisReport)

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT_TEMPLATE)
        ])

        logger.info(f"AnalystAgent initialized with model: {self.model_name}")

    async def analyze(self, state: GameState) -> AnalysisReport:
        """
        Builds the full prompt, sends it to OpenAI via LangChain,
        and returns a structured AnalysisReport with tactical recommendations.

        Prompt assembly is delegated to build_prompt_variables() in prompts.py
        — all prompt logic lives in one place, agent stays focused on its job.

        Raises specific OpenAI exceptions so main.py can return
        the correct HTTP status code to the client.
        """
        try:
            prompt_vars = build_prompt_variables(state)
            print(prompt_vars["game_summary_text"])
            logger.info(
                f"Prompt built — {state.home_team.name} vs {state.away_team.name} "
                f"| Period {state.current_period} "
                f"| Objective: {state.directives.game_objective}"
            )

            chain = self.prompt_template | self.llm
            report = await chain.ainvoke(prompt_vars)

            logger.info(
                f"Analysis complete — {len(report.recommended_actions)} recommendations "
                f"(confidence: {report.confidence_score})"
            )
            return report

        except AuthenticationError:
            logger.error("OpenAI authentication failed — check BA_OPENAI_API_KEY in .env")
            raise

        except RateLimitError:
            logger.warning("OpenAI rate limit hit")
            raise

        except APITimeoutError:
            logger.error("OpenAI request timed out")
            raise

        except APIConnectionError:
            logger.error("Could not connect to OpenAI — check network connectivity")
            raise

        except Exception as e:
            # exc_info=True logs the full stack trace, not just the message
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            raise