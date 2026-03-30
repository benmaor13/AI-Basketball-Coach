
GAME_STATE_EXAMPLE = {
    "venue_type": "Home",
    "home_score": 88,
    "away_score": 82,
    "current_period": 4,
    "minutes_remaining": 3,
    "seconds_remaining": 45,
    "possession": "Home",
    "home_timeouts_remaining": 2,
    "away_timeouts_remaining": 1,
    "home_team_fouls": 3,
    "away_team_fouls": 5,
    "rules": {
        "league_format": "FIBA",
        "number_of_periods": 4,
        "period_length_minutes": 10,
        "overtime_length_minutes": 5,
        "max_fouls_per_player": 5,
        "team_fouls_to_penalty": 4,
        "shot_clock_seconds": 24,
        "offensive_rebound_reset_seconds": 14,
        "max_timeouts": 5
    },
    "momentum": {
        "overall_trend": "Strong Home",
        "home_team_run": 8,
        "away_team_run": 0,
        "crowd_intensity": "Electric"
    },
    "directives": {
        "primary_strategy": "Pace and Space",
        "defensive_focus": "Force Turnovers",
        "risk_tolerance": "High",
        "game_objective": "Win at all costs"
    },
    "home_team": {
        "name": "BGU Lakers",
        "league_position": 1,
        "win_streak": 3,
        "offensive_rank": 2,
        "defensive_rank": 4,
        "timeouts_remaining": 2,
        "team_fouls": 3,
        "upcoming_schedule_density": "High",
        "players": [
            {"name": "Noam", "number": 7, "age": 24, "position": "PG", "is_on_court": True, "current_fouls": 2, "minutes_played": 32, "fatigue_level": "Normal", "field_goals_made": 5, "field_goals_attempted": 10, "three_pointers_made": 2, "three_pointers_attempted": 4, "free_throws_made": 4, "free_throws_attempted": 4, "rebounds": 3, "assists": 8, "steals": 2, "blocks": 0, "turnovers": 3, "position_rank": 1}
            # ... שאר השחקנים ...
        ]
    },
    "away_team": {
        "name": "Away Town Ballers",
        # ... שאר הנתונים ...
    }
}
# app/schemas/examples.py

ANALYSIS_REPORT_EXAMPLE = {
    "summary": "Home team is leading by 6 with under 4 minutes left. The momentum is positive, but the away team's point guard is exploiting the drop coverage.",
    "main_threat": "Away team's #30 is scoring easily off high pick-and-rolls due to a lack of aggressive defensive pressure.",
    "recommended_actions": [
        {
            "action_type": "Defensive Shift",
            "description": "Switch from drop coverage to blitzing the pick-and-roll against #30.",
            "expected_impact": "Force the ball out of the primary scorer's hands and make their role players beat you.",
            "priority": "High",
            "involved_player_numbers": [23, 1]
        },
        {
            "action_type": "Substitution",
            "description": "Sub out tired big man #15 for quicker defender #8.",
            "expected_impact": "Better mobility to execute the blitz and recover to the perimeter.",
            "priority": "Medium",
            "involved_player_numbers": [15, 8]
        }
    ],
    "risk_assessment": "Blitzing will leave the roll man temporarily open, requiring perfect weak-side rotations to prevent easy layups.",
    "confidence_score": 0.92
}