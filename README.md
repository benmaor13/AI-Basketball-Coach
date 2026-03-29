# BasketballAI

AI-powered tactical advisor designed to help basketball coaches make data-backed decisions under pressure. By analyzing live game data such as scores, fouls, and momentum it provides real-time recommendations for substitutions, defensive adjustments, and timeout strategies.

## MVP Status
The core logic was previously validated in a local environment. This repository represents a refactor into a ready MVP(work in progress).

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI (Asynchronous)
* **Validation:** Pydantic V2 
* **AI:** OpenAI **GPT-4o**

## Project Structure
* **`app/`** – Main application directory:
    * **`main.py`** – Entry point for the FastAPI server.
    * **`models/`** – Pydantic V2 schemas (GameState, AnalysisResult, etc.).
    * **`agents/`** – AI reasoning logic and prompt management.
    * **`core/`** – Application settings and central configuration.
* **`requirements.txt`** – Project dependencies.
* **`.env.example`** – Template for required environment variables (API keys, etc.).
