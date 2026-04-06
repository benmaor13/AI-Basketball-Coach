"""
Prompt templates for the AnalystAgent.

Design principles:
- System prompt covers only what the AI cannot know from training:
  our custom data format, hard rules specific to this system, and
  reasoning/output requirements. No generic basketball knowledge.
- Directive instructions live in USER prompt (they change per call).
- Conditional fields only appear in the summary when relevant.
  The AI has no memory — absence is invisible, not a gap.
- Every instruction references only stats actually visible in the
  prompt for that specific directive/scenario.
  """
# Directive Instruction Dictionaries
# Translate clean CoachDirectives literals into tactical AI commands.
# Each instruction references ONLY stats visible in the prompt for that scenario.

OFFENSIVE_STRATEGY_INSTRUCTIONS = {
    # 3PT% shown when Pace & Space is active — safe to reference
    "Pace & Space": (
        "Sub in 'Sharpshooter' style players with the highest 3PT% (visible in player lines). "
        "Push fast breaks after every defensive stop."
    ),
    # FT% shown when Attack the Paint is active — safe to reference
    # Opponent foul counts visible in [ACTIONABLE ALERTS]
    "Attack the Paint": (
        "Sub in 'Slasher' and 'Post Threat' style players. "
        "If opponent is in PENALTY, draw fouls aggressively. "
        "Target opponents flagged in [ACTIONABLE ALERTS] with high foul counts."
    ),
    # EFF always visible — safe to reference
    "Pick & Roll Heavy": (
        "Pair the highest EFF PG(prefer 'Floor General' style) with the highest EFF C(make a sub if needed)."
    ),
    # EFF always visible — safe to reference
    "Feed the Post": (
        "Isolate the highest EFF and style 'Post Threat' C or PF in the post."
    ),
    # EFF always visible — safe to reference
    "Motion Offense": (
        "Balance the floor. Prioritize overall team EFF. "
        "Favor 'Versatile' and 'Floor General' style players."
    ),
    "Auto": "Use your basketball judgment based on the current game state and personnel.",
}

DEFENSIVE_FOCUS_INSTRUCTIONS = {
    # Style always visible — BLK not shown, rely on Style only
    "Protect the Paint": (
        "Sub in 'Rim Protector' style players. "
        "They are specifically chosen for rim protection — trust the Style field."
    ),
    # Style always visible — STL not shown, rely on Style only
    "Deny Perimeter": (
        "Sub in 'Wing Defender' style players. "
        "They are built to chase shooters off the 3-point line."
    ),
    # Style always visible — STL not shown, rely on Style only
    "Blitz & Trap": (
        "Sub in 'Wing Defender' style players who apply defensive pressure. "
        "Double-team ball handlers aggressively."
    ),
    # Style and Fouls always visible
    "Switch Everything": (
        "Sub in 'Versatile' style players who can defend multiple positions. "
        "Avoid 'Rim Protector' style C or PF — they cannot switch onto perimeter players. "
        "Avoid players with high fouls — switching increases foul exposure."
    ),
    # Style and Fatigue always visible
    "Zone Defense": (
        "Prioritize 'Rim Protector' and 'Post Threat' style for size. "
        "Effective for managing fatigue — zone requires less individual effort."
    ),
    "Auto": "Use your basketball judgment based on the opponent threat and current lineup.",
}

RISK_TOLERANCE_INSTRUCTIONS = {
    # Fatigue and Fouls X/limit always visible — safe to reference both
    # Describe foul threshold relationally (within N of limit) not as a variable
    "Low": (
        "Sub out any player marked Tired or Exhausted, regardless of Rank status. "
        "Sub out any player whose fouls are within 2 of their limit (e.g. Fouls:3/5 or Fouls:4/6)."
    ),
    "Medium": (
        "Rest role players (Rank > 1) when Tired or approaching foul limit(e.g. Rank:2 and Fouls:3/5). "
        "Stretch Rank:1 stars — they may stay if Tired but not Exhausted. "
        "Sub out Rank:1 stars when fouls are within 1 of their limit (e.g. Fouls:4/5), unless Game Phase:CLUTCH TIME."
    ),
    "High": (
        "Keep Rank:1 stars on court regardless of fatigue, unless they are Injured. "
        "Only sub out Rank:1 stars when fouls are within 1 of their limit (e.g. Fouls:4/5) AND it is not Game Phase:CLUTCH TIME."
    ),
}

GAME_OBJECTIVE_INSTRUCTIONS = {
    # EFF and Rank always visible
    "Win Now": (
    "Play Rank:1 players only. Do NOT sub out a Rank:1 player for rest, "
    "fatigue management, or strategic preservation — these are long-term "
    "considerations that contradict Win Now. "
    "Only sub out Rank:1 players if they are Injured, in foul trouble "
    "(fouls within 1 of limit), or marked Exhausted. "
    "Bench Rank:2 players unless forced by the above conditions."
),
    # Age visible when Develop Youth is active — safe to reference
    # [DEVELOPMENT OPPORTUNITY] alert fires when this objective is active
    "Develop Youth": (
        "Mandatory: sub in all U25 players listed in [DEVELOPMENT OPPORTUNITY]. "
        "Accept lower EFF — development overrides efficiency logic."
    ),
    # FT% visible when Kill the Clock is active — safe to reference
    "Kill the Clock": (
        "Sub in players with the highest FT% (visible in player lines). "
        "Run the full shot clock on every possession. "
        "Avoid low FT% players — they become a liability when intentionally fouled."
    ),
    # 3PT% visible when Desperate Comeback is active — safe to reference
    "Desperate Comeback": (
        "Sub in 'Sharpshooter' style players with the highest 3PT% (visible in player lines). "
        "Push pace. Use Foul Strategy to stop the clock and recover possessions. "
        "Ignore fatigue management."
    ),
    "Auto": "Determine the appropriate objective from the game context — score, time, momentum, and personnel.",
}


# System Prompt
SYSTEM_PROMPT = """
You are an elite basketball tactical analyst. You receive a structured game state and deliver a precise, data-driven AnalysisReport to the coach. Every recommendation must be specific and immediately actionable — not generic basketball advice.

DATA FORMAT
The game state uses a custom format. These fields are specific to this system: 

Rank:N — position_rank, where Rank:1 is the best player at that specific position on this team. Higher number = lower priority.
EFF — custom game efficiency score calculated from all player stats this game. Higher is better.
Fouls shown as current/limit — e.g., 4/5 means one more foul = disqualification.
Style — the player's tactical archetype. Use this to match players to the active directive.
CLUTCH TIME / Late Close Game / Regular Flow — explicit game phase label. CLUTCH TIME is the strongest urgency signal.
WE / OPPONENT in momentum — perspective-aware.
"WE are on a X point run" means we have outscored them by X points recently.
"OPPONENT on a X point run" means they have outscored us by X points recently.
A 7 point run is significant momentum — treat it with the same urgency as a 7-0 run.

HARD RULES
No exception regardless of context:
- Never sub in a player listed in [UNAVAILABLE PERSONNEL].
- Never invent player names or numbers not present in the summary.
- Every [ACTIONABLE ALERT] must be addressed — address as many as possible within the action limit, prioritizing: Mandatory Subs are more important.
- When multiple substitutions are needed, handle them sequentially — 
  identify the outgoing player's position, find the best available 
  bench player for that position, assign them, then move to the next 
  substitution. Each bench player can only be used once across all 
  substitutions in the same report — before assigning a bench player, 
  verify they have not already been used in a previous substitution.
-Position group match takes priority over style match. First find a bench 
  player in the correct position group, then within that group choose the 
  best style match for the active directive. Only if no position match 
  exists should you cross positions.
- A player can only be subbed in if they appear in 
  [AVAILABLE BENCH PERSONNEL]. Players in [ON COURT PERSONNEL] 
  are already playing and cannot be subbed in.
- Never recommend more than one Timeout action in a single report — 
  only one timeout can be called per stoppage of play.
  Only include actions that tell the coach to DO something. 
-Never include actions framed as "avoid X" or "do not X" — 
these are not recommendations, they are observations. 
State them in risk_assessment instead.
  
MOMENTUM
Note that A scoring run in [STRATEGIC CONTEXT] is a valid standalone trigger for a Timeout even without an [ACTIONABLE ALERT]:
- "OPPONENT on a X points run" → breaking their rhythm by calling a Timeout is a legitimate tactics.
- "WE are on a X points run" → avoid unnecessary changes that disrupt momentum.

DIRECTIVE INSTRUCTIONS
The user message contains specific tactical instructions for each active directive.
They define which Styles, stats, and priorities to use when making decisions.
Apply them within the constraints of hard rules and actionable alerts —
directives guide your choices, they do not override mandatory situations.
Game Objective is the meta-goal and can override other directives.
Risk Tolerance governs all fatigue and foul decisions.

OUTPUT STRUCTURE & REASONING

Fill each TacticalAction in this exact order — reasoning must be written
before choosing action_type:

reasoning → written FIRST. Must:
            - cite the section it came from
            ([ACTIONABLE ALERTS], [STRATEGIC CONTEXT]...)
            - Reference specific values (EFF, Fouls X/limit, Fatigue,
              Style, game phase)
            - Justify through one of:
              1. An [ACTIONABLE ALERT] that requires a response
              2. A directive instruction that guides the choice
              3. A game state observation that creates a tactical opportunity
            - Connect directly to the specific action being recommended

Then fill in order: action_type → description → expected_impact → priority
→ involved_player_numbers

involved_player_numbers:
  Substitution  → [OUT_jersey, IN_jersey] exactly two numbers, always this order
  Foul Strategy → [TARGET_jersey] when targeting a specific player, [] if general
  All other types → [] (empty)
  
Return one action per [ACTIONABLE ALERT] as a minimum. After addressing 
all alerts, always check the active Game Objective directive for 
additional tactical recommendations before finishing.


─────────────────────────────────────────
EXAMPLE — alert-driven TacticalAction:
─────────────────────────────────────────
reasoning:       "Per [STRATEGIC CONTEXT], Risk Tolerance is High — Rank:1 stars stay
                 on court unless Injured. However [ACTIONABLE ALERTS] flags Avi Mizrahi
                 (#15) as Exhausted (Fouls:2/5, Rank:1), which crosses the threshold even
                 at High risk per the Risk Tolerance directive. Dor Eliyahu (#22, PF, Fresh)
                 is available in [AVAILABLE BENCH PERSONNEL] to restore defensive energy
                 for the final 3 minutes of CLUTCH TIME."
action_type:     "Substitution"
description:     "Sub out #15, bring in #22."
expected_impact: "Restores defensive intensity at PF without disrupting positional structure."
priority:        "High"
involved_player_numbers: [15, 22]

─────────────────────────────────────────
EXAMPLE — observation-driven TacticalAction:
─────────────────────────────────────────
reasoning:       "John Doe (#30, SG) appears in [OPPONENT THREAT ON COURT] with EFF:18
                 and Fouls:4/5 — one more foul disqualifies him. No alert flagged this
                 but the data presents a clear opportunity. Running pick-and-roll actions
                 directly at him forces defensive effort and increases foul risk."
action_type:     "Foul Strategy"
description:     "Direct pick-and-roll actions toward #30 every possession."
expected_impact: "Forces his 5th foul and removes the opponent's primary scorer."
priority:        "Medium"
involved_player_numbers: [30]
"""

USER_PROMPT_TEMPLATE = """\
{game_summary_text}

DIRECTIVE INSTRUCTIONS
Apply strictly. They define which players to prioritize and how to decide.

Offensive Strategy — {offensive_strategy}:
{offensive_strategy_instruction}

Defensive Focus — {defensive_focus}:
{defensive_focus_instruction}

Risk Tolerance — {risk_tolerance}:
{risk_tolerance_instruction}

Game Objective — {game_objective}:
{game_objective_instruction}
{retry_context}
"""

# Prompt variable builder
# All prompt logic lives here — AnalystAgent just calls this function.
def build_prompt_variables(state, previous_report=None) -> dict:
    """
    Assembles all variables for the user prompt template.
    Both the directive label (e.g. "Attack the Paint") and its tactical
    instruction are injected — label gives context, instruction gives commands.
    If previous_report is provided, retry context is injected into the prompt.
    """
    d = state.directives

    # Build retry context if this is a retry attempt
    if previous_report:
        retry_context = (
            f"\nRETRY CONTEXT\n"
            f"Your previous analysis had low confidence ({previous_report.confidence_score}).\n"
            f"You identified: {previous_report.self_critique}\n\n"
            f"Before revising, explicitly verify each of these:\n"
            f"1. Count the alerts in [ACTIONABLE ALERTS] — have you addressed every single one?\n"
            f"2. Check each substitution — is the incoming player in [AVAILABLE BENCH PERSONNEL — ONLY THESE PLAYERS CAN BE SUBBED IN]?\n"
            f"3. Check positions — does each substitution match position groups (PG/SG, SF/PF, C/PF)?\n"
            f"4. Have you checked [OPPONENT THREAT ON COURT] for observation-driven opportunities?\n"
            f"5. Is your action count at least equal to the number of alerts?\n\n"
            f"Now provide a revised AnalysisReport addressing any gaps found above.\n"
        )
    else:
        retry_context = ""

    return {
        "game_summary_text": state.to_ai_summary(),
        "offensive_strategy": d.offensive_strategy,
        "defensive_focus": d.defensive_focus,
        "risk_tolerance": d.risk_tolerance,
        "game_objective": d.game_objective,
        "offensive_strategy_instruction": OFFENSIVE_STRATEGY_INSTRUCTIONS[d.offensive_strategy],
        "defensive_focus_instruction": DEFENSIVE_FOCUS_INSTRUCTIONS[d.defensive_focus],
        "risk_tolerance_instruction": RISK_TOLERANCE_INSTRUCTIONS[d.risk_tolerance],
        "game_objective_instruction": GAME_OBJECTIVE_INSTRUCTIONS[d.game_objective],
        "retry_context": retry_context,
    }