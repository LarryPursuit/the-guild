"""SQLAlchemy models: User, Guild, Quest and Reward.

Relationships:
- A User owns many Guilds, is assigned many Quests and earns many Rewards.
- A Guild has many Quests (deleting a guild deletes its quests).
- A Quest has at most one Reward. Deleting a quest keeps the reward in the
  user's inventory (its quest_id is set to NULL).
"""
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .game import rank_for_xp


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    character_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    guilds: Mapped[list["Guild"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    quests: Mapped[list["Quest"]] = relationship(back_populates="user")
    rewards: Mapped[list["Reward"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def rank(self) -> str:
        return rank_for_xp(self.xp)


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="guilds")
    quests: Mapped[list["Quest"]] = relationship(
        back_populates="guild", cascade="all, delete-orphan", order_by="Quest.id"
    )

    @property
    def open_quests(self) -> int:
        return sum(1 for q in self.quests if q.status == "open")

    @property
    def completed_quests(self) -> int:
        return sum(1 for q in self.quests if q.status == "completed")


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), default="easy")  # easy | medium | hard
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="open")  # open | completed
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    guild: Mapped["Guild"] = relationship(back_populates="quests")
    user: Mapped["User"] = relationship(back_populates="quests")
    reward: Mapped["Reward | None"] = relationship(back_populates="quest", uselist=False)


class Reward(Base):
    """An item earned for completing a quest. Stores the raw D&D 5e API response."""

    __tablename__ = "rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quest_id: Mapped[int | None] = mapped_column(ForeignKey("quests.id"), nullable=True, unique=True)
    item_index: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(200))
    item_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    api_response: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="rewards")
    quest: Mapped["Quest | None"] = relationship(back_populates="reward")
