# BasketballAI 🏀

I built this project because I wanted to combine two things I care about — basketball and AI — into something that actually solves a real problem. Coaches make split-second decisions under pressure with a lot of information to process. This system tries to help with that.

You feed it the current game state and it tells you what to do — who to sub, whether to call a timeout, how to adjust your defense. It reasons through the situation the way a tactical analyst would, not just pattern-matching on stats.

---

## What it actually does

A coach sends the current game state to the API mid-game. The system looks at everything — score, time, which players are on the court, their foul counts and fatigue, what the opponent's top scorer is doing, what the coach's strategy is — and returns concrete recommendations ranked by urgency.

Not "consider resting your center" — more like "sub out #11, he has 4 fouls out of 5 and the opponent's best scorer is targeting him. Bring in #22 who's fresh and can cover that matchup."

Each recommendation comes with the reasoning behind it and the expected impact. The overall analysis includes a confidence score and self-critique so the coach knows how much to trust the full set of recommendations.

---

## Current limitation worth knowing

Right now the coach has to manually fill in the full game state — player stats, foul counts, fatigue levels, score, everything — and send it as a JSON request. That's obviously not practical during an actual game.

The plan is to build a live interface where the coach (or an assistant on the sideline) just presses buttons as things happen — player gets a foul, someone looks tired, score changes — and the state updates automatically in the background. When the coach wants advice they just hit a button and the analysis runs against the current state. For now though, the input is manual, and the focus has been on getting the reasoning and output quality right before building the UI layer on top.

---

## Tech Stack

- **Python / FastAPI** — async API, handles the real-time nature of the use case
- **Pydantic V2** — deep validation across all the models (more on this below)
- **LangChain + OpenAI GPT-4o** — structured output via `with_structured_output()` so the AI returns typed Pydantic objects, not raw text
- **pydantic-settings** — clean config management with .env support

---

## Project Structure

```
app/
├── main.py                  
├── models/
│   ├── player.py            
│   ├── team.py              
│   ├── game_state.py        # the core — validates game logic and builds the AI prompt
│   ├── league_rules.py      # FIBA / NBA / NCAA (rules auto-apply based on format)
│   ├── game_momentum.py     
│   ├── coach_directives.py  
│   ├── analysis_result.py   # the structured output schema
│   └── examples.py          # pre-built test scenarios
├── agents/
│   ├── analyze_part.py      # self-evaluating agent with confidence-based retry loop
│   └── prompts.py           # system prompt + directive instructions + prompt builder
└── core/
    ├── config.py            
    ├── constants.py         
    └── logger.py            
tests/
├── test_validators.py       # custom model_validator tests
└── test_game_state.py       # game flags and smoke tests
```

---

## Things I'm proud of

**The prompt isn't just a JSON dump.** `to_ai_summary()` builds a structured natural-language summary with labeled sections — `[ACTIONABLE ALERTS]`, `[ON COURT PERSONNEL]`, `[OPPONENT THREAT]`, etc. Fields like FT%, 3PT%, and Age only show up when they're actually relevant to the situation, which keeps the prompt lean and the AI focused on what matters right now.

**The validation layer is real.** It's not just type checking. The system validates that foul counts don't exceed league limits, that momentum trends are consistent with scoring runs, that you can't have a fouled-out player still on the court, that timeouts don't exceed the league maximum. It knows the difference between FIBA and NBA rules and enforces them automatically.

**Single source of truth for live stats.** Timeouts remaining and team fouls are owned by `GameState`, not by the individual team objects. Sounds small but it prevents a whole class of subtle bugs where validation uses one value and the AI prompt uses another.

**Self-evaluating agent with autonomous retry.** The system returns a `confidence_score` with every analysis and a `self_critique` explaining any uncertainty. If confidence falls below 0.70, the agent autonomously retries — injecting its own self_critique into the next prompt so the retry is targeted, not random. No human involvement between calls. On complex scenarios with many simultaneous alerts, the retry consistently catches missed recommendations that the first pass overlooked.

---

## MVP Status

The core logic was originally built and tested locally across a range of game scenarios. This repo is a full refactor of that into a clean, structured API — proper validation, async endpoints, logging, environment config, and a prompt system that's been thought through carefully.

It works end to end: game state comes in, gets validated, the AI reasons through it, structured recommendations come out. The agent evaluates its own output and retries autonomously when uncertain.

---

## How to Run

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Set up your environment:**
```bash
cp .env.example .env   # on Windows: copy .env.example .env
```
Open `.env` and add your OpenAI API key:
```
BA_OPENAI_API_KEY=your_key_here
BA_MODEL_NAME=gpt-4o
```

**3. Start the server:**
```bash
uvicorn app.main:app --reload
```

**4. Open the interactive docs:**
```
http://localhost:8000/docs
```
Click **POST /analyze → Try it out → Execute** to run your first analysis. The example is pre-filled automatically.

---

## Pre-Built Test Scenarios

The project includes 4 game scenarios covering different tactical situations. The Swagger UI loads whichever example is active in `game_state.py`.

To switch scenarios, change one line in `app/models/game_state.py`:

```python
model_config = ConfigDict(
    json_schema_extra={"example": GAME_STATE_EXAMPLE}  # swap this constant
)
```

And make sure it's imported at the top of the same file:

```python
from .examples import GAME_STATE_EXAMPLE  # replace with whichever you need
```

| Scenario | Constant | Situation |
|---|---|---|
| Win Now | `GAME_STATE_EXAMPLE` | Leading by 6, CLUTCH TIME, star in foul trouble |
| Desperate Comeback | `DESPERATE_COMEBACK_EXAMPLE` | Losing by 10, last 1:45, Pace & Space active |
| Develop Youth | `DEVELOP_YOUTH_EXAMPLE` | Leading by 14, period 2, full U25 bench |
| Retry Loop | `RETRY_IMPROVEMENT_EXAMPLE` | Leading by 4, 7 simultaneous alerts, Late Close Game |
---

## Running the Tests

From the project root directory:
```bash
pytest tests/ -v
```

Tests cover the custom game logic validators, league rule overrides, and game phase detection — not library behavior. The goal was testing code I actually wrote, not Pydantic's built-in constraints.

---

## Environment Variables

```
BA_OPENAI_API_KEY=your_key_here
BA_MODEL_NAME=gpt-4o
```

---

## Roadmap

**Live sideline UI** — a simple interface where an assistant updates the game state by pressing buttons as things happen rather than filling in JSON. The analysis would run against the live state whenever the coach asks for it. This is the most important next step — it transforms the system from a developer API into something a real coach could actually use.

**Game memory** — tracking recommendations across a full game so the AI doesn't repeat itself or contradict earlier advice it gave in the same game.

**Deployment** — a live URL so the system can be tested without cloning the repo or setting up an API key.
