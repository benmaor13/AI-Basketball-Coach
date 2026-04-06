# Constants that are used to define specific game states and analyze the situation.
# A game is "clutch time" when it's the last period or overtime,under 2 minutes,
# and score difference is not more than 6 points
CLUTCH_TIME_MINUTES = 2
CLUTCH_TIME_MAX_SCORE_DIFF = 6

# "Late close game" is a wider window  than clutch game - last period or overtime,under 4 minutes, within ~3 possessions
LATE_GAME_MINUTES = 4
LATE_GAME_MAX_SCORE_DIFF = 11

# Substitutions logic
# Minimum minutes a player must play after subbing in before being subbed out again.
# Prevents rapid yo-yo substitutions that disrupt rhythm.
MIN_STINT_MINUTES = 2.0

# Foul threshold diff from max — how close to fouling out triggers a warning to the coach
# In first half: 3 fouls from the limit
# In second half: 1 foul from the limit
FOUL_TROUBLE_BUFFER_FIRST_HALF = 3
FOUL_TROUBLE_BUFFER_SECOND_HALF = 1

# Foul threshold diff from max — how close to fouling out triggers a warning to the coach (regarding stars of the team)
STAR_PLAYER_FOUL_TROUBLE_BUFFER = 1

# Foul threshold diff from max — how close to fouling out of opponent player triggers notifying the coach
OPPONENT_FOUL_TROUBLE_BUFFER = 2

# Players under this age are considered "youth" for development objectives
YOUTH_AGE_THRESHOLD = 25
# Autonomous retry loop thresholds
CONFIDENCE_RETRY_THRESHOLD = 0.7 # retry if confidence below this
MAX_ANALYSIS_RETRIES = 2           # max retry attempts before accepting best result

# A scoring run of this many points or more is considered a significant momentum shift
SIGNIFICANT_RUN_THRESHOLD = 6