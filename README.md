# BasketballAI 🏀

I built this project because I wanted to combine two things I care about — basketball and AI — into something that actually solves a real problem. Coaches make split-second decisions under pressure with a lot of information to process. This system tries to help with that.

You feed it the current game state and it tells you what to do — who to sub, whether to call a timeout, how to adjust your defense. It reasons through the situation the way a tactical analyst would, not just pattern-matching on stats.

---

## What it actually does

A coach sends the current game state to the API mid-game. The system looks at everything — score, time, which players are on the court, their foul counts and fatigue, what the opponent's top scorer is doing, what the coach's strategy is — and returns concrete recommendations ranked by urgency.

Not "consider resting your center" — more like "sub out #11, he has 4 fouls out of 5 and the opponent's best scorer is targeting him. Bring in #22 who's fresh and can cover that matchup."

Each recommendation comes with the reasoning behind it, the expected impact, and a confidence score so the coach knows how much to trust it.

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
│   ├── game_state.py       
│   ├── league_rules.py    
│   ├── game_momentum.py     
│   ├── coach_directives.py  
│   ├── analysis_result.py   
│   └── examples.py          
├── agents/
│   ├── analyze_part.py     
│   └── prompts.py           
└── core/
    ├── config.py            
    ├── constants.py         
    └── logger.py            
```


## MVP Status

The core logic was originally built and tested locally across a range of game scenarios. This repo is a full refactor of that into a clean, structured API — proper validation, async endpoints, logging, environment config, and a prompt system that's been thought through carefully rather than bolted on.

It works end to end: game state comes in, gets validated, the AI reasons through it, structured recommendations come out.


---

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env
# add your OpenAI key to .env
uvicorn app.main:app --reload
```

Then go to `http://localhost:8000/docs` — there's a full example pre-loaded in Swagger so you can run your first analysis immediately.

---

## Environment Variables

```
BA_OPENAI_API_KEY=your_key_here
BA_MODEL_NAME=gpt-4o-mini
```
