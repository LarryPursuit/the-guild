"""Demo adventurers: a fresh, pre-filled account for anyone who wants to try The Guild without registering.

Each demo account is separate, so visitors never see or change each other's boards.
It has a random, unknown password, so the only way in is the demo button.
"""
import secrets
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .auth import hash_password

NAMES = ["Mira", "Thorne", "Wren", "Kael", "Isolde", "Bram", "Sable", "Orrin", "Lyra", "Fenn"]

# (guild name, charter, [(title, details, difficulty, due in days or None, completed?)])
GUILDS = [
    ("Job Hunt Guild", "Applications, interviews and portfolio work", [
        ("Finish the Project 2 pitch", "Slides, demo script and a two-minute rehearsal.", "hard", 3, False),
        ("Apply to 3 jobs", None, "hard", -2, False),
        ("Update LinkedIn", "New headline and the Project 1 case study.", "easy", None, False),
        ("Mock interview with a peer", None, "medium", -5, True),
    ]),
    ("Iron Body Guild", "Training, sleep and proper meals", [
        ("Run 5k", None, "medium", 1, False),
        ("Meal prep for the week", None, "easy", None, True),
    ]),
    ("Scholars' Circle", "Courses, reading and practice problems", [
        ("Finish chapter 4 of SICP", None, "medium", 4, False),
        ("20 practice problems", "Arrays and hash maps.", "hard", 9, False),
    ]),
]

# Loot already in the pack, as if earned from the completed quests above (and one earlier quest).
LOOT = [
    ("spyglass", "Spyglass", "Adventuring Gear"),
    ("rations-1-day", "Rations (1 day)", "Adventuring Gear"),
    ("longsword", "Longsword", "Weapon"),
]
STARTING_XP = 85  # just short of Silver, so the first cleared quest shows a promotion
STARTING_CLASS = "Ranger"


def _unique_username(db: Session) -> str:
    for _ in range(20):
        name = f"{secrets.choice(NAMES)}-{secrets.randbelow(9000) + 1000}"
        if not db.scalar(select(models.User.id).where(models.User.username == name)):
            return name
    return f"Adventurer-{secrets.token_hex(4)}"


def create_demo_user(db: Session) -> models.User:
    username = _unique_username(db)
    user = models.User(
        username=username,
        email=f"{username.lower()}-{secrets.token_hex(3)}@demo.theguild.invalid",
        password_hash=hash_password(secrets.token_urlsafe(24)),
        character_class=STARTING_CLASS,
        xp=STARTING_XP,
    )
    db.add(user)
    db.flush()

    today = date.today()
    now = datetime.now(timezone.utc)
    completed = []
    for name, charter, quests in GUILDS:
        guild = models.Guild(name=name, description=charter, owner_id=user.id)
        db.add(guild)
        db.flush()
        for title, details, difficulty, due_in, done in quests:
            quest = models.Quest(
                guild_id=guild.id,
                user_id=user.id,
                title=title,
                description=details,
                difficulty=difficulty,
                due_date=today + timedelta(days=due_in) if due_in is not None else None,
                status="completed" if done else "open",
                completed_at=now - timedelta(days=1) if done else None,
            )
            db.add(quest)
            if done:
                completed.append(quest)
    db.flush()

    for i, (index, name, category) in enumerate(LOOT):
        db.add(models.Reward(
            user_id=user.id,
            quest_id=completed[i].id if i < len(completed) else None,
            item_index=index,
            item_name=name,
            item_category=category,
            api_response={"index": index, "name": name, "equipment_category": {"name": category}, "demo": True},
        ))

    db.commit()
    db.refresh(user)
    return user
