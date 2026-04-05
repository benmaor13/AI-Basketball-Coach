from fastapi import FastAPI, HTTPException
from openai import RateLimitError, APITimeoutError, APIConnectionError
from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport
from app.agents.analyze_part import AnalystAgent
from app.core.logger import get_logger

# Initialize Logger for main.py
logger = get_logger(__name__)
# instance of the FastAPI
app = FastAPI(
    title="BasketballAI API",
    description="Real-time tactical analysis system for basketball coaches",
    version="1.0.0"
)
# Initialize the Agent
agent = AnalystAgent()
@app.get("/")
async def health_check():
    """Server check"""
    return {
        "status": "online",
        "system": "BasketballAI",
        "agent_model": agent.model_name
    }

@app.post("/analyze", response_model=AnalysisReport)
async def perform_analysis(state: GameState):
    """Perform tactical analysis on game state"""
    try:
        report = await agent.analyze(state)
        return report

    except RateLimitError:
        # 429: Too Many Requests
        raise HTTPException(
            status_code=429,
            detail="AI service is currently overloaded. Please try again shortly."
        )
    except APITimeoutError:
        # 504: Gateway Timeout
        raise HTTPException(
            status_code=504,
            detail="AI service timed out. Please try again."
        )
    except APIConnectionError:
        # 503: Service Unavailable
        raise HTTPException(
            status_code=503,
            detail="Could not reach AI service. Please check your network connection."
        )
    except Exception as e:
        # 500: Internal Server Error
        # We use exc_info=True here because we don't know what caused this error
        logger.error(f"Unexpected error in /analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during tactical analysis."
        )