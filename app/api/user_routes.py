# Standard Library Imports
import hashlib  # For hashing functions
import hmac  # For HMAC (hash-based message authentication code)
import json  # For JSON parsing
import urllib.parse  # For URL parsing and decoding

# Third-Party Imports
from fastapi import APIRouter, HTTPException, Depends, Request, \
    status  # FastAPI components for routing and error handling
from pydantic import BaseModel  # Pydantic for data validation
from sqlalchemy.ext.asyncio import AsyncSession  # SQLAlchemy for asynchronous database operations
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

# Local Application Imports
from app.schemas import User, UserRole, UserBase, UserQuestProgress, RoleSelection  # User data validation schema
from app.crud import get_user_by_tID, create_user, delete_user_by_id, assign_initial_quests, assign_initial_achievements  # CRUD operations
from app.database import get_db  # Database session dependency

router = APIRouter()  # Create an APIRouter instance for handling routes


# Endpoint to verify initial data and handle user authentication
@router.get("/users")
async def get_user_data(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Verify the initial data received from the client.

    - **request**: The incoming request containing headers.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the user along with their quest progress and redirects to the profile page.
    """

    # Access validated params from /utils/auth_middleware
    validated_params = request.state.validated_params


    # Extract user data after validation
    user_data_str = validated_params.get('user', '')
    user_data = json.loads(user_data_str) if user_data_str else {}

    # Map the received field names to the model's expected names if needed
    user_data['telegram_id'] = user_data.pop('id')
    user_data['is_premium'] = False
    user_data['user_class'] = 'Mage'

    existing_user = await get_user_by_tID(db, user_data.get('telegram_id'))


    if existing_user:
        user_data_response = {
            "id": str(existing_user.id),
            "telegram_id": existing_user.telegram_id,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "username": existing_user.username,
            "user_class": existing_user.user_class,
            "level": existing_user.level,
            "points": existing_user.points,
            "coins": existing_user.coins,
            "quests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "started_at": progress.started_at,
                    "completed_at": progress.completed_at,
                    "is_locked": progress.is_locked
                }
                for progress in existing_user.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "image_url": achievement.achievement.image_url,
                    "is_locked": achievement.is_locked
                }
                for achievement in existing_user.achievements
            ]
        }

        return {"user": user_data_response, "redirect": "/profile", "message": "User already exists, user data from db"}
    else:
        return {"redirect": "/choose-role", "message": "Please choose a role to complete your registration."}


@router.post("/users")
async def create_user_after_role_selection(
        role_selection: RoleSelection,  # Extracting the role from the request body
        request: Request,  # Retrieving user data from the Authorization header
        db: AsyncSession = Depends(get_db)
):
    """
    Create a new user after the role has been selected.

    - **role_selection**: The data containing the selected role (received from the request body).
    - **request**: The incoming request containing headers.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the created user and redirects to the profile page.
    """

    # Access validated params from /utils/auth_middleware
    validated_params = request.state.validated_params

    # Extract user data after validation
    user_data_str = validated_params.get('user', '')
    user_data = json.loads(user_data_str) if user_data_str else {}

    # Map the received field names to the model's expected names if needed
    user_data['telegram_id'] = user_data.pop('id')
    user_data['is_premium'] = False
    user_data['user_class'] = 'Mage'

    # Add the selected role to the user data
    user_data['role'] = role_selection.role

    # Check if the user exists in the database
    existing_user = await get_user_by_tID(db, user_data.get('telegram_id'))

    if existing_user:
        # Existing user case
        user_data_response = {
            "id": str(existing_user.id),
            "telegram_id": existing_user.telegram_id,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "username": existing_user.username,
            "user_class": existing_user.user_class,
            "level": existing_user.level,
            "points": existing_user.points,
            "coins": existing_user.coins,
            "quests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "started_at": progress.started_at,
                    "completed_at": progress.completed_at,
                    "is_locked": progress.is_locked
                }
                for progress in existing_user.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "image_url": achievement.achievement.image_url,
                    "is_locked": achievement.is_locked
                }
                for achievement in existing_user.achievements
            ]
        }
        return {"user": user_data_response, "redirect": "/profile",
                "message": "User already exists, preventing multiple user creation!"}
    else:
        # Create the new user with the selected role
        new_user = await create_user(db, UserBase(**user_data))

        # Assign initial quests and achievements
        await assign_initial_quests(db, new_user.id)
        await assign_initial_achievements(db, new_user.id)

        # Fetch the newly created user data
        new_user_data = await get_user_by_tID(db, user_data.get('telegram_id'))

        user_data_response = {
            "id": str(new_user_data.id),
            "telegram_id": new_user_data.telegram_id,
            "first_name": new_user_data.first_name,
            "last_name": new_user_data.last_name,
            "username": new_user_data.username,
            "user_class": new_user_data.user_class,
            "level": new_user_data.level,
            "points": new_user_data.points,
            "coins": new_user_data.coins,
            "quests": [
                {
                    "id": str(progress.quest.id),
                    "name": progress.quest.name,
                    "status": progress.status,
                    "progress": progress.progress,
                    "started_at": progress.started_at,
                    "completed_at": progress.completed_at,
                    "is_locked": progress.is_locked
                }
                for progress in new_user_data.quest_progress
            ],
            "achievements": [
                {
                    "id": str(achievement.id),
                    "name": achievement.achievement.name,
                    "description": achievement.achievement.description,
                    "image_url": achievement.achievement.image_url,
                    "is_locked": achievement.is_locked,
                    "status": achievement.status
                }
                for achievement in new_user_data.achievements
            ]

        }
        return {"user": user_data_response, "redirect": "/profile",
                "message": "User created successfully with selected role. Initial quests have been assigned."}


# Endpoint to delete a user by ID
@router.delete("/users/{user_id}")
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
