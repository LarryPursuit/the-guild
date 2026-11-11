"""Quest CRUD, completing quests (XP + rank) and item rewards from the D&D 5e API."""
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import dnd_api, models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..game import XP_BY_DIFFICULTY
from ..serializers import user_out
from .guilds import get_owned_guild

router = APIRouter(prefix="/api", tags=["quests"])


def get_owned_quest(quest_id: int, user: models.User, db: Session) -> models.Quest:
    quest = db.get(models.Quest, quest_id)
    if quest is None or quest.guild.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Quest not found.")
    return quest


def grant_reward(db: Session, user: models.User, quest: models.Quest) -> tuple[models.Reward | None, str | None]:
    """Fetch a random item from the D&D 5e API and save the response as a Reward.

    Returns (reward, None) on success or (None, error message) if the API fails.
    A failed reward never undoes the quest completion.
    """
    try:
        item = dnd_api.random_equipment()
    except dnd_api.DndApiError as exc:
        return None, f"{exc} Your quest is saved; you can claim the reward later."

    reward = models.Reward(
        user_id=user.id,
        quest_id=quest.id,
        item_index=item["index"],
        item_name=item["name"],
        item_category=(item.get("equipment_category") or {}).get("name"),
        api_response=item,
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward, None


@router.get("/guilds/{guild_id}/quests", response_model=list[schemas.QuestOut])
def list_quests(
    guild_id: int,
    status_filter: Literal["open", "completed"] | None = Query(default=None, alias="status"),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_guild(guild_id, user, db)
    stmt = select(models.Quest).where(models.Quest.guild_id == guild_id)
    if status_filter:
        stmt = stmt.where(models.Quest.status == status_filter)
    stmt = stmt.order_by(models.Quest.due_date.is_(None), models.Quest.due_date, models.Quest.id)
    return db.scalars(stmt).all()


@router.post("/guilds/{guild_id}/quests", response_model=schemas.QuestOut, status_code=status.HTTP_201_CREATED)
def create_quest(
    guild_id: int,
    data: schemas.QuestCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_guild(guild_id, user, db)
    quest = models.Quest(guild_id=guild_id, user_id=user.id, **data.model_dump())
    quest.title = quest.title.strip()
    db.add(quest)
    db.commit()
    db.refresh(quest)
    return quest


@router.get("/quests/{quest_id}", response_model=schemas.QuestOut)
def read_quest(quest_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_owned_quest(quest_id, user, db)


@router.patch("/quests/{quest_id}", response_model=schemas.QuestOut)
def update_quest(
    quest_id: int,
    data: schemas.QuestUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quest = get_owned_quest(quest_id, user, db)
    changes = data.model_dump(exclude_unset=True)
    if quest.status == "completed" and "difficulty" in changes and changes["difficulty"] != quest.difficulty:
        raise HTTPException(status_code=400, detail="You can't change the difficulty of a completed quest.")
    for field in ("title", "difficulty"):
        if field in changes and changes[field] is None:
            raise HTTPException(status_code=400, detail=f"Quest {field} can't be empty.")
    for field, value in changes.items():
        setattr(quest, field, value.strip() if field == "title" else value)
    db.commit()
    db.refresh(quest)
    return quest


@router.delete("/quests/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quest(quest_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    quest = get_owned_quest(quest_id, user, db)
    db.delete(quest)  # the reward (if any) stays in the inventory with quest_id = NULL
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/quests/{quest_id}/complete", response_model=schemas.QuestCompleteOut)
def complete_quest(quest_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    quest = get_owned_quest(quest_id, user, db)
    if quest.status == "completed":
        raise HTTPException(status_code=400, detail="This quest is already complete.")

    old_rank = user.rank
    xp_gained = XP_BY_DIFFICULTY[quest.difficulty]
    quest.status = "completed"
    quest.completed_at = datetime.now(timezone.utc)
    user.xp += xp_gained
    db.commit()  # save XP first so an API failure can't lose it

    reward, reward_error = grant_reward(db, user, quest)
    db.refresh(quest)
    db.refresh(user)
    return schemas.QuestCompleteOut(
        quest=schemas.QuestOut.model_validate(quest),
        xp_gained=xp_gained,
        user=user_out(user),
        ranked_up=user.rank != old_rank,
        reward=schemas.RewardOut.model_validate(reward) if reward else None,
        reward_error=reward_error,
    )


@router.post("/quests/{quest_id}/reward", response_model=schemas.RewardOut, status_code=status.HTTP_201_CREATED)
def claim_reward(quest_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retry the item reward for a completed quest whose reward failed earlier."""
    quest = get_owned_quest(quest_id, user, db)
    if quest.status != "completed":
        raise HTTPException(status_code=400, detail="Complete the quest before claiming its reward.")
    if quest.reward is not None:
        raise HTTPException(status_code=409, detail="This quest's reward was already claimed.")
    reward, reward_error = grant_reward(db, user, quest)
    if reward is None:
        raise HTTPException(status_code=503, detail=reward_error)
    return reward
