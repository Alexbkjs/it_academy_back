from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class UpdateUserClassRequest(BaseModel):
    userClass: str


class UpdateUserProfileDetailsRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    user_class: Optional[str] = None
    level: Optional[int] = None
    coins: Optional[int] = None
    points: Optional[int] = None


class UserRoleModel(BaseModel):
    id: UUID
    role_name: str

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population


class UserRoleResponse(BaseModel):
    role_name: str  # Only return the role_name field

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly


class UserRoleCreate(BaseModel):
    role: str


class QuestBase(BaseModel):
    type: str
    name: str
    image_url: str = Field(..., alias="imageUrl", description="URL of the quest image")
    description: str
    award: str
    goal: str
    requirements: str
    required_level: int = Field(
        ..., alias="requiredLevel", description="Level to accept the quest"
    )
    long_description: str

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


class QuestPatchUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    description: Optional[str] = None
    award: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class QuestCreateResponse(QuestBase):
    id: UUID
    created_at: datetime = Field(None, alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class QuestUpdateResponse(QuestBase):
    id: UUID
    created_at: datetime = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class QuestsResponse(BaseModel):
    message: str
    quests: List[Quest]
    total: int  # Total number of quests available


class InitialQuestResponse(BaseModel):
    message: str
    quest: Quest


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
    coins: int = 0
    points: int = 0
    level_increase: int = 0


class Reward(RewardBase):
    id: UUID
    quest_id: UUID

    class Config:
        from_attributes = True


# UserQuestProgress schema
class UserQuestProgressBase(BaseModel):
    status: str
    progress: float
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    is_locked: bool = Field(True, alias="isLocked")
    mentor_comment: Optional[str] = Field(..., alias="mentorComment")
    is_reward_accepted: bool = Field(False, alias="isRewardAccepted")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class UserQuestProgress(UserQuestProgressBase):
    id: UUID
    quest_id: UUID
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    quest: Optional[Quest] = None  # Nested Quest model

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class UserQuestProgressResponse(UserQuestProgressBase):
    id: UUID
    quest_id: UUID = Field(..., alias="questId")
    user_id: UUID = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class UserQuestProgressChangesRequest(BaseModel):
    mentor_comment: str


# Achievement schema
class AchievementBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = Field(None, alias="imageUrl")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class Achievement(AchievementBase):
    id: UUID
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


# UserAchievement schema
class UserAchievementBase(BaseModel):
    status: str  # "active" or "blocked"
    is_locked: bool = Field(False, alias="isLocked")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using field names for population


class UserAchievement(UserAchievementBase):
    id: UUID
    user_id: UUID
    achievement_id: UUID
    achievement: Optional[Achievement] = None  # Nested Achievement model

    class Config:
        from_attributes = True


# User schema
class UserBase(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    username: Optional[str] = None
    user_class: Optional[str] = Field(None, alias="userClass")
    image_url: Optional[str] = Field(
        "https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/ava6.jpg",
        alias="imageUrl",
    )
    level: int = Field(0, alias="level")
    points: int = Field(0, alias="points")
    coins: int = Field(0, alias="coins")
    # Now role is an object instead of just role_id
    role: UserRoleResponse
    # role_id: UUID  # Change to string to match incoming role value

    quest_progress: List[UserQuestProgress] = Field([], alias="userQuests")
    achievements: List[UserAchievement] = Field([], alias="userAchievements")

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population


class UserCreate(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    username: Optional[str] = None
    user_class: Optional[str] = Field(None, alias="userClass")
    image_url: Optional[str] = Field(
        "https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/ava6.jpg",
        alias="imageUrl",
    )
    level: int = Field(0, alias="level")
    points: int = Field(0, alias="points")
    coins: int = Field(0, alias="coins")
    # Now role is an object instead of just role_id
    # role: Optional[UserRoleModel] = None
    role_id: UUID  # Change to string to match incoming role value

    quest_progress: List[UserQuestProgress] = Field([], alias="userQuests")
    achievements: List[UserAchievement] = Field([], alias="userAchievements")

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population


class User(UserBase):
    id: UUID
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population


class UserResponse(BaseModel):
    message: Optional[str] = None  # The message field is now optional
    user: User

    class Config:
        from_attributes = True  # Enables Pydantic to work with ORM objects directly
        populate_by_name = True  # Allow using field names for population
