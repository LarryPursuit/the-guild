"""The logged-in adventurer's profile, inventory and the list of D&D classes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import dnd_api, models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..serializers import user_out

router = APIRouter(prefix="/api", tags=["adventurer"])


@router.get("/users/me", response_model=schemas.UserOut)
def read_me(user: models.User = Depends(get_current_user)):
    return user_out(user)


@router.patch("/users/me", response_model=schemas.UserOut)
def update_me(
    data: schemas.UserUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.character_class is not None:
        # Only accept real classes from the D&D 5e API.
        try:
            valid = {c["index"]: c["name"] for c in dnd_api.list_classes()}
        except dnd_api.DndApiError as exc:
            raise HTTPException(status_code=503, detail=f"{exc} Try again in a moment.")
        if data.character_class not in valid:
            raise HTTPException(status_code=400, detail="That is not a valid D&D class.")
        user.character_class = valid[data.character_class]
    db.commit()
    db.refresh(user)
    return user_out(user)


@router.get("/rewards", response_model=list[schemas.RewardOut])
def list_rewards(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """The adventurer's inventory, newest first."""
    stmt = (
        select(models.Reward)
        .where(models.Reward.user_id == user.id)
        .order_by(models.Reward.created_at.desc(), models.Reward.id.desc())
    )
    return db.scalars(stmt).all()


@router.get("/classes", response_model=list[schemas.DndClassOut])
def list_classes(user: models.User = Depends(get_current_user)):
    try:
        return dnd_api.list_classes()
    except dnd_api.DndApiError as exc:
        raise HTTPException(status_code=503, detail=f"{exc} Try again in a moment.")
