from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    Boolean,
    Float,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
import uuid
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String, unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    user_class = Column(String, nullable=True)
    image_url = Column(
        String,
        nullable=False,
        default="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/ava6.jpg",
    )
    level = Column(Integer, default=1)
    points = Column(Integer, default=100)
    coins = Column(Integer, default=1000)
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("user_roles.id"), nullable=True
    )  # ForeignKey reference
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    achievements = relationship(
        "UserAchievementModel", cascade="all, delete", back_populates="user"
    )
    quest_progress = relationship(
        "UserQuestProgress", cascade="all, delete", back_populates="user"
    )
    # Relationship to user roles
    role = relationship("UserRoleModel")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    image_url = Column(String, default="")
    description = Column(String, default="")
    award = Column(String, default="")
    goal = Column(String, default="")
    requirements = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    requirements_table = relationship("Requirement", back_populates="quest")
    rewards = relationship("Reward", back_populates="quest")
    quest_progress = relationship("UserQuestProgress", back_populates="quest")
    initial_quest = relationship("InitialQuest", back_populates="quest", uselist=False)


class InitialQuest(Base):
    __tablename__ = "initial_quests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id = Column(UUID(as_uuid=True), ForeignKey("quests.id"), unique=True)

    # Relationship to the Quest table
    quest = relationship("Quest", back_populates="initial_quest")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    users = relationship("UserAchievementModel", back_populates="achievement")


class UserAchievementModel(Base):
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False
    )
    status = Column(
        String, nullable=False, default="active"
    )  # Either "active" or "blocked"
    is_locked = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")


class UserQuestProgress(Base):
    __tablename__ = "user_quest_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quest_id = Column(
        UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False
    )  # Corrected ForeignKey
    status = Column(String, nullable=False)
    progress = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_locked = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    user = relationship("User", back_populates="quest_progress")
    quest = relationship("Quest", back_populates="quest_progress")


class Requirement(Base):
    __tablename__ = "requirements_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    quest_id = Column(
        UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False
    )  # Corrected ForeignKey

    quest = relationship("Quest", back_populates="requirements_table")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    quest_id = Column(
        UUID(as_uuid=True), ForeignKey("quests.id"), nullable=False
    )  # Corrected ForeignKey

    quest = relationship("Quest", back_populates="rewards")
