"""Pydantic schemas: what the API accepts (…Create / …Update) and returns (…Out)."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Difficulty = Literal["easy", "medium", "hard"]


# ---------- Auth & users ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        # bcrypt only accepts up to 72 bytes; non-ASCII characters use more than one byte each.
        if len(v.encode()) > 72:
            raise ValueError("Password is too long (72 bytes max)")
        return v

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v or v.startswith("@") or v.endswith("@"):
            raise ValueError("Enter a valid email address")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def username_clean(cls, v: str) -> str:
        v = v.strip()
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only use letters, numbers, - and _")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    character_class: str | None
    xp: int
    rank: str
    next_rank: str | None = None
    next_rank_xp: int | None = None
    created_at: datetime | None = None
    quests_completed: int = 0


class UserUpdate(BaseModel):
    character_class: str | None = Field(default=None, max_length=50)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Guilds ----------
class GuildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class GuildUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class GuildOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    owner_id: int
    open_quests: int
    completed_quests: int
    created_at: datetime


# ---------- Rewards ----------
class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quest_id: int | None
    item_index: str
    item_name: str
    item_category: str | None
    created_at: datetime


# ---------- Quests ----------
class QuestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    difficulty: Difficulty = "easy"
    due_date: date | None = None


class QuestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    difficulty: Difficulty | None = None
    due_date: date | None = None


class QuestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guild_id: int
    title: str
    description: str | None
    difficulty: Difficulty
    due_date: date | None
    status: Literal["open", "completed"]
    completed_at: datetime | None
    created_at: datetime
    reward: RewardOut | None = None


class QuestCompleteOut(BaseModel):
    """Result of completing a quest. reward is None when the D&D API call failed."""

    quest: QuestOut
    xp_gained: int
    user: UserOut
    ranked_up: bool
    reward: RewardOut | None
    reward_error: str | None = None


class DndClassOut(BaseModel):
    index: str
    name: str
