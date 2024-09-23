# Standard Library Imports
import hashlib  # For hashing functions
import hmac  # For HMAC (hash-based message authentication code)
import json  # For JSON parsing
import urllib.parse  # For URL parsing and decoding

# Third-Party Imports
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Request,
    status,
)  # FastAPI components for routing and error handling
from pydantic import BaseModel  # Pydantic for data validation
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)  # SQLAlchemy for asynchronous database operations
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

# Local Application Imports
from app.schemas import (
    User,
    UserRole,
    UserBase,
    UserQuestProgress,
    RoleSelection,
)  # User data validation schema
from app.crud import (
    get_user_by_tID,
    create_user,
    delete_user_by_id,
    assign_initial_quests,
    assign_initial_achievements,
)  # CRUD operations
from app.database import get_db  # Database session dependency

router = APIRouter()  # Create an APIRouter instance for handling routes


# Endpoint to verify initial data and handle user authentication
@router.get("/user")
async def get_user_data(request: Request, db: AsyncSession = Depends(get_db)):
    validated_params = request.state.validated_params
    user_data_str = validated_params.get("user", "")
    user_data = json.loads(user_data_str) if user_data_str else {}

    existing_user = await get_user_by_tID(db, user_data.get("id"))

    if existing_user:
        user_data_response = {
            "id": str(existing_user.id),
            "telegramId": existing_user.telegram_id,
            "firstName": existing_user.first_name,
            "lastName": existing_user.last_name,
            "username": existing_user.username,
            "role": existing_user.role,
            "imageUrl": existing_user.image_url,
            "level": existing_user.level,
            "points": existing_user.points,
            "coins": existing_user.coins,
            "activeQuests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "startedAt": progress.started_at,
                    "completedAt": progress.completed_at,
                    "isLocked": progress.is_locked,
                    "quest": {
                        "id": progress.quest.id,
                        "name": progress.quest.name,
                        "description": progress.quest.description,
                        "goal": progress.quest.goal,
                        "award": progress.quest.award,
                        "imageUrl": progress.quest.image_url,
                        "createdAt": progress.quest.created_at,
                        "updatedAt": progress.quest.updated_at,
                    },
                }
                for progress in existing_user.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "imageUrl": achievement.achievement.image_url,
                    "isLocked": achievement.is_locked,
                }
                for achievement in existing_user.achievements
            ],
        }

        return {
            "redirect": "/profile",
            "message": "User already exists, returning user data from database",
            "user": user_data_response,
        }

    else:
        raise HTTPException(
            status_code=401,
            detail="Please choose a role to complete your registration.",
        )


@router.post("/user")
async def create_user_after_role_selection(
    role_selection: RoleSelection,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    validated_params = request.state.validated_params
    user_data_str = validated_params.get("user", "")
    user_data = json.loads(user_data_str) if user_data_str else {}

    user_data["telegram_id"] = user_data.pop("id")
    user_data["role"] = role_selection.role

    existing_user = await get_user_by_tID(db, user_data.get("telegram_id"))

    if existing_user:
        user_data_response = {
            "id": str(existing_user.id),
            "telegramId": existing_user.telegram_id,
            "firstName": existing_user.first_name,
            "lastName": existing_user.last_name,
            "username": existing_user.username,
            "role": existing_user.role,
            "imageUrl": existing_user.image_url,
            "level": existing_user.level,
            "points": existing_user.points,
            "coins": existing_user.coins,
            "activeQuests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "startedAt": progress.started_at,
                    "completedAt": progress.completed_at,
                    "isLocked": progress.is_locked,
                    "quest": {
                        "id": progress.quest.id,
                        "name": progress.quest.name,
                        "description": progress.quest.description,
                        "goal": progress.quest.goal,
                        "award": progress.quest.award,
                        "imageUrl": progress.quest.image_url,
                        "createdAt": progress.quest.created_at,
                        "updatedAt": progress.quest.updated_at,
                    },
                }
                for progress in existing_user.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "imageUrl": achievement.achievement.image_url,
                    "isLocked": achievement.is_locked,
                }
                for achievement in existing_user.achievements
            ],
        }

        return {
            "user": user_data_response,
            "redirect": "/profile",
            "message": "User already exists, preventing multiple user creation!",
        }

    else:
        new_user = await create_user(db, UserBase(**user_data))
        await assign_initial_quests(db, new_user.id)
        await assign_initial_achievements(db, new_user.id)

        new_user_data = await get_user_by_tID(db, user_data.get("telegram_id"))

        user_data_response = {
            "id": str(new_user_data.id),
            "telegramId": new_user_data.telegram_id,
            "firstName": new_user_data.first_name,
            "lastName": new_user_data.last_name,
            "username": new_user_data.username,
            "role": new_user_data.role,
            "imageUrl": "https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/ava6.jpg",
            "level": new_user_data.level,
            "points": new_user_data.points,
            "coins": new_user_data.coins,
            "activeQuests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "startedAt": progress.started_at,
                    "completedAt": progress.completed_at,
                    "isLocked": progress.is_locked,
                    "quest": {
                        "id": progress.quest.id,
                        "name": progress.quest.name,
                        "description": progress.quest.description,
                        "goal": progress.quest.goal,
                        "award": progress.quest.award,
                        "imageUrl": progress.quest.image_url,
                        "createdAt": progress.quest.created_at,
                        "updatedAt": progress.quest.updated_at,
                    },
                }
                for progress in new_user_data.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "imageUrl": achievement.achievement.image_url,
                    "isLocked": achievement.is_locked,
                    "status": achievement.status,
                }
                for achievement in new_user_data.achievements
            ],
        }

        return {
            "redirect": "/profile",
            "message": "User created successfully with selected role. Initial quests have been assigned.",
            "user": user_data_response,
        }


# Endpoint to delete a user by ID
@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a user by their ID.

    - **user_id**: The ID of the user to delete.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user is deleted, or raises a 404 error if not found.
    """
    user_deleted = await delete_user_by_id(db, user_id)
    if user_deleted:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
