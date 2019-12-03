"""
Score module
"""

import nativecards.lib.settings as config


def calc_score(attempt) -> int:
    """
    Calculates and returns the attempt score
    """
    score = 100 // config.get('attempts_to_remember', attempt.card.created_by)
    if attempt.is_hint:
        attempt.hints_count = max(1, attempt.hints_count)
        if attempt.is_correct:
            score = score // (attempt.hints_count + 1)
        else:
            score = score * (attempt.hints_count + 1)

    return score if attempt.is_correct else -score
