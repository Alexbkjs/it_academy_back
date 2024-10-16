# Standard Library Imports
import json  # For JSON parsing

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

# Local Application Imports

from app.crud import delete_user_by_id  # CRUD operations
from app.database import get_db  # Database session dependency
from app.models import User as UserModel
from app.utils.get_current_user import get_current_user


router = APIRouter()  # Create an APIRouter instance for handling routes


@router.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Fetches all users from the database.

    - db: AsyncSession for performing database operations.

    Returns a list of users.
    """
    result = await db.execute(select(UserModel))

    users = result.scalars().all()

    return {"message": "Users data fetched from the database", "users": users}


@router.get("/users/{user_id}")
async def get_user_by_tg_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetches get user from the database by user_id == telegram_id.

    - ***db***: AsyncSession for performing database operation.

    Return selected user.

    """

    result = await db.execute(select(UserModel).where(UserModel.telegram_id == user_id))

    user = result.scalar_one_or_none()

    if user:

        return user
    else:
        raise HTTPException(404, "User Not Found")


# Endpoint to delete a user by ID
@router.delete("/users/{user_id}")
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


@router.put("/users/{user_id}")
async def update_all_information(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Change all information in selected user by their ID.

    - **user_id**: The ID of the user to put information.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user information changed, or raises a 404 error if not found.
    """
    result = await db.execute(select(UserModel).where(UserModel.telegram_id == user_id))

    user_info = result.scalar_one_or_none()

    if not user_info:
        raise HTTPException(404, "User not found")

    new_user_data = await request.json()

    user_info.first_name = new_user_data["first_name"]
    user_info.last_name = new_user_data["last_name"]
    user_info.username = new_user_data.get("username")
    user_info.user_class = new_user_data.get("user_class")
    user_info.level = new_user_data["level"]
    user_info.points = new_user_data["points"]
    user_info.coins = new_user_data["coins"]

    await db.commit()

    return {"message": "User information successfully replaced", "user": user_info}


@router.patch("/users/{user_id}")
async def update_selected_information(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Change some selected information in selected user by their ID.

    - **user_id**: The ID of the user to put information.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user selected information changed, or raises a 404 error if not found.
    """
    result = await db.execute(select(UserModel).where(UserModel.telegram_id == user_id))

    user_info = result.scalar_one_or_none()

    new_user_data = await request.json()
    if not user_info:
        raise HTTPException(404, "User not found")

    available_fields = [
        "first_name",
        "last_name",
        "username",
        "user_class",
        "level",
        "coins",
        "points",
    ]

    for field in available_fields:
        if field in new_user_data:
            setattr(user_info, field, new_user_data[field])

    await db.commit()

    return {"message": "User information successfully replaced", "user": user_info}
