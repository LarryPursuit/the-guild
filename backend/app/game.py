"""Game rules: how much XP a quest is worth and which rank a total XP earns.

Kept in one place so the numbers are easy to tune after real use.
"""

XP_BY_DIFFICULTY = {"easy": 10, "medium": 25, "hard": 50}

# (minimum XP, rank name), lowest first.
RANKS = [(0, "Copper"), (100, "Silver"), (300, "Gold"), (600, "Mythril")]


def rank_for_xp(xp: int) -> str:
    rank = RANKS[0][1]
    for threshold, name in RANKS:
        if xp >= threshold:
            rank = name
    return rank


def next_rank_info(xp: int) -> dict:
    """Return the next rank and how much XP it needs, or None values at the top rank."""
    for threshold, name in RANKS:
        if xp < threshold:
            return {"next_rank": name, "next_rank_xp": threshold}
    return {"next_rank": None, "next_rank_xp": None}
