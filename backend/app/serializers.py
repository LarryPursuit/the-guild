"""Helpers that turn models into response schemas when extra fields are needed."""
from . import models, schemas
from .game import next_rank_info


def user_out(user: models.User) -> schemas.UserOut:
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        character_class=user.character_class,
        xp=user.xp,
        rank=user.rank,
        created_at=user.created_at,
        quests_completed=sum(1 for q in user.quests if q.status == "completed"),
        **next_rank_info(user.xp),
    )
