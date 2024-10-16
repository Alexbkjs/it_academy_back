# Standard Library Imports
import json  # For JSON parsing
from typing import List
from uuid import UUID

# Third-Party Imports
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Request,
    status,
)  # FastAPI components for routing and error handling

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)  # SQLAlchemy for asynchronous database operations
from sqlalchemy import select, update

# Local Models Imports
from app.models import User as UserModel

# Local Application Imports
from app.schemas import (
    UserBase as User,
    UserResponse,
    UserRoleCreate,
    UserCreate,
    UpdateUserClassRequest
)  # User data validation schema
from app.crud import (
    get_user_by_tID,
    create_user,
    delete_user_by_id,
    assign_initial_quests,
    assign_initial_achievements,
    complete_quest_and_take_rewards,
)  # CRUD operations
from app.database import get_db  # Database session dependency
from app.models import UserRoleModel, User as UserModel
from app.utils.get_current_user import get_current_user

from app.utils.role_check import role_required

router = APIRouter()  # Create an APIRouter instance for handling routes


# @router.put("/user/class", response_model=UserResponse) // getting validation error
@router.put("/user/class")
async def update_user_class(
    request: Request,
    update_data: UpdateUserClassRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate user class
    if update_data.userClass not in ["frontend", "designer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user class. Choose either 'frontend' or 'designer'.",
        )
    # Update the user class directly
    update_class_query = (
        update(UserModel)
        .where(UserModel.id == current_user.id)
        .values(user_class=update_data.userClass)
    )
    await db.execute(update_class_query)

    # Commit the change
    await db.commit()
    updated_user = await get_current_user(request, db)

    # Return the updated user
    return {"message": "User was updated successfully", "user": updated_user}


# Endpoint to verify initial data and handle user authentication
@router.get("/user", response_model=UserResponse)
async def get_user_data(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Fetches user data from the database based on the Telegram ID.
    Raises an exception if the user does not exist and prompts role selection.

    - **request**: The HTTP request object containing validated params.
    - **db**: AsyncSession for performing database operations.

    Returns a dictionary containing the message and the user data if found.
    Raises an HTTPException if the user is not found.
    """

    # Use the get_current_user function to retrieve the user
    current_user = await get_current_user(request, db)
    if current_user:
        # If the user exists, return a success message along with their data
        return {
            "message": "User data fetched from the database",
            "user": current_user,
        }
    else:
        # If no user is found, raise an HTTP 401 error and request role selection
        raise HTTPException(
            status_code=401,
            detail="Please choose a role to complete your registration.",
        )

# Endpoint to delete a user by ID
@router.delete("/user/{user_id}")
@role_required(["adventurer"])  # Temporary solution for testing purposes to be able to remove the user from db via frontend
async def delete_user(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
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


