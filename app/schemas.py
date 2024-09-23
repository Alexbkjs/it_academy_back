from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# Enum for UserRole
class UserRole(str, Enum):
    adventurer = "adventurer"
    avatar = "avatar"
    kingdom = "kingdom"


class RoleSelection(BaseModel):
    role: UserRole


# Quest schema

# Example Use Cases
# Creating a New Quest: Use QuestBase for the request body.
# Retrieving Quest Details: Use Quest for the response, which includes the additional fields.

class QuestBase(BaseModel):

    name: str
    image_url: HttpUrl = Field(..., alias="imageUrl",  description="URL of the quest image")
    description: str
    award: str
    goal: str
    requirements: str

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population


class Quest(QuestBase):
    id: UUID
    created_at: datetime = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class QuestsResponse(BaseModel):
    quests: List[Quest]
    total: int  # Total number of quests available



# Requirement schema
class RequirementBase(BaseModel):
    description: str
    class Config:
        from_attributes = True


class Requirement(RequirementBase):
    id: UUID
    quest_id: UUID

    class Config:
        from_attributes = True


# Reward schema
class RewardBase(BaseModel):
    description: str


class Reward(RewardBase):
    id: UUID
    quest_id: UUID

    class Config:
        from_attributes = True


# UserQuestProgress schema
class UserQuestProgressBase(BaseModel):
    status: str
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_locked: bool = True


class UserQuestProgress(UserQuestProgressBase):
    id: UUID
    quest_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    quest: Optional[Quest] = None  # Nested Quest model

    class Config:
        from_attributes = True


# Achievement schema
class AchievementBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None


class Achievement(AchievementBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# UserAchievement schema
class UserAchievementBase(BaseModel):
    status: str  # "active" or "blocked"
    is_locked: bool = False


class UserAchievement(UserAchievementBase):
    id: UUID
    user_id: UUID
    achievement_id: UUID
    achievement: Optional[Achievement] = None  # Nested Achievement model

    class Config:
        from_attributes = True


# User schema
class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    user_class: Optional[str] = None
    image_url: Optional[str] = (
        "https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/ava6.jpg"
    )
    level: int = 1
    points: int = 100
    coins: int = 1000
    role: Optional[UserRole] = None

    quest_progress: List[UserQuestProgress] = []  # Nested UserQuestProgress
    achievements: List[UserAchievement] = []  # Nested UserAchievement


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
