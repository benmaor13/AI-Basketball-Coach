from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import RateLimitError, APITimeoutError, APIConnectionError, AuthenticationError
from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport
from app.agents.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_prompt_variables
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.constants import CONFIDENCE_RETRY_THRESHOLD, MAX_ANALYSIS_RETRIES

logger = get_logger(__name__)


class AnalystAgent:
    """
    Responsible for the connection with openai
    """
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
        Autonomous analysis loop with confidence-based retry.
        On each attempt, builds the prompt and calls OpenAI via LangChain.
        If confidence falls below CONFIDENCE_RETRY_THRESHOLD in constants.py, the agent
        autonomously retries(using the self.critique that is always made)
        the next prompt so the retry is targeted, not random.
        No human involvement between attempts. Returns the best result
        if the threshold is never reached after MAX_ANALYSIS_RETRIES.
        Raises specific OpenAI exceptions so main.py can return
        the correct HTTP status code to the client.
        """
        try:
            best_report = None
            attempt = 0

            while attempt <= MAX_ANALYSIS_RETRIES:
                is_retry = attempt > 0

                # On retry, pass previous report so self_critique will be used
                prompt_vars = build_prompt_variables(
                    state,
                    previous_report=best_report if is_retry else None
                )
                if not is_retry:
                    logger.info(
                        f"Prompt built — {state.home_team.name} vs {state.away_team.name} "
                        f"| Period {state.current_period} "
                        f"| Objective: {state.directives.game_objective}"
                    )
                else:
                    logger.warning(
                        f"Retrying analysis (retry {attempt} of {MAX_ANALYSIS_RETRIES}) "
                        f"— previous confidence: {best_report.confidence_score}"
                    )

                chain = self.prompt_template | self.llm
                report = await chain.ainvoke(prompt_vars)
                logger.info(
                    f"Attempt {attempt + 1} complete — "
                    f"{len(report.recommended_actions)} recommendations "
                    f"(confidence: {report.confidence_score})"
                )

                # Always keep the best result across attempts
                if best_report is None or report.confidence_score > best_report.confidence_score:
                    best_report = report

                # Accept if confidence threshold is met
                if report.confidence_score >= CONFIDENCE_RETRY_THRESHOLD:
                    logger.info(
                        f"Analysis accepted on attempt {attempt + 1} "
                        f"(confidence: {report.confidence_score})"
                    )
                    return best_report

                attempt += 1

            # reached the maximum retries — return best result achieved till now
            logger.warning(
                f"Max retries reached — returning best result "
                f"(confidence: {best_report.confidence_score})"
            )
            return best_report
        # Handling errors
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