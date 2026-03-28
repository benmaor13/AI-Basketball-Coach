from fastapi import FastAPI, HTTPException
from app.models.game_state import GameState
from app.models.analysis_result import AnalysisReport
from app.agents.analyze_part import AnalystAgent

app = FastAPI(
    title="BasketballAI API",
    description="Real-time tactical analysis system for basketball coaches",
    version="1.0.0"
)
agent = AnalystAgent()
@app.get("/")
async def health_check():
    """Server  check"""
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

    except Exception as e:
        # If something goes wrong in our logic or AI, we return a 500 error
        raise HTTPException(
            status_code=500,
            detail=f"Error during tactical analysis: {str(e)}"
        )
# NOTE: Run the server using: uvicorn app.main:app --reload