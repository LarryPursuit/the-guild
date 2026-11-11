"""Guild CRUD. Users can only see and change the guilds they own (MVP)."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/guilds", tags=["guilds"])


def get_owned_guild(guild_id: int, user: models.User, db: Session) -> models.Guild:
    """Return the guild if it exists and belongs to the user; otherwise 404.

    We return 404 (not 403) for other people's guilds so we don't reveal they exist.
    """
    guild = db.get(models.Guild, guild_id)
    if guild is None or guild.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Guild not found.")
    return guild


@router.get("", response_model=list[schemas.GuildOut])
def list_guilds(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(models.Guild).where(models.Guild.owner_id == user.id).order_by(models.Guild.id)
    return db.scalars(stmt).all()


@router.post("", response_model=schemas.GuildOut, status_code=status.HTTP_201_CREATED)
def create_guild(
    data: schemas.GuildCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    guild = models.Guild(name=data.name.strip(), description=data.description, owner_id=user.id)
    db.add(guild)
    db.commit()
    db.refresh(guild)
    return guild


@router.get("/{guild_id}", response_model=schemas.GuildOut)
def read_guild(guild_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_owned_guild(guild_id, user, db)


@router.patch("/{guild_id}", response_model=schemas.GuildOut)
def update_guild(
    guild_id: int,
    data: schemas.GuildUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    guild = get_owned_guild(guild_id, user, db)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] is None:
        raise HTTPException(status_code=400, detail="Guild name can't be empty.")
    for field, value in changes.items():
        setattr(guild, field, value.strip() if isinstance(value, str) and field == "name" else value)
    db.commit()
    db.refresh(guild)
    return guild


@router.delete("/{guild_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guild(guild_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    guild = get_owned_guild(guild_id, user, db)
    db.delete(guild)  # cascades to the guild's quests; their rewards stay in the inventory
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
