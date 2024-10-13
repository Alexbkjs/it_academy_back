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
)  # FastAPI components for routing and error handling

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)  # SQLAlchemy for asynchronous database operations
from sqlalchemy.future import select

# Local Models Imports
from app.models import User as UserModel

# Local Application Imports
from app.schemas import (
    UserBase,
    UserResponse,
    UserRoleCreate,
    UserCreate,
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
from app.models import UserRoleModel

from app.utils.role_check import role_required

router = APIRouter()  # Create an APIRouter instance for handling routes


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

    # Extract validated params from the request (e.g., from middleware)
    validated_params = request.state.validated_params

    # Retrieve the 'user' data string from the validated params, if it exists
    user_data_str = validated_params.get("user", "")

    # Parse the user data string into a dictionary, or use an empty dict if not found
    user_data = json.loads(user_data_str) if user_data_str else {}

    # Attempt to fetch the existing user from the database using their Telegram ID
    existing_user = await get_user_by_tID(db, user_data.get("id"))

    if existing_user:
        # If the user exists, return a success message along with their data
        return {
            "message": "User data fetched from the database",
            "user": existing_user,
        }
    else:
        # If no user is found, raise an HTTP 401 error and request role selection
        raise HTTPException(
            status_code=401,
            detail="Please choose a role to complete your registration.",
        )


@router.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Fetches all users from the database.

    - db: AsyncSession for performing database operations.

    Returns a list of users.
    """

    query = select(UserModel)
    result = await db.execute(query)
    users = result.scalars().all()

    return {"message": "Users data fetched from the database", "users": users}


@router.get("/users/{user_id}")
async def get_user_by_tg_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetches get user from the database by user_id == telegram_id.

    - ***db***: AsyncSession for performing database operation.

    Return selected user.

    """

    query = select(UserModel).where(UserModel.telegram_id == user_id)
    query_result = await db.execute(query)
    user = query_result.scalar_one_or_none()

    if user:

        return user
    else:
        raise HTTPException(404, "User Not Found")


@router.post("/users", response_model=UserResponse)
async def create_user_after_role_selection(
    role_selected_by_user: UserRoleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Retrieve role from the UserRoleModel
    role = await db.execute(
        select(UserRoleModel).where(
            UserRoleModel.role_name == role_selected_by_user.role
        )
    )
    role = role.scalars().first()

    if not role:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    # Retrieve validated params from the request state
    validated_params = request.state.validated_params
    user_data_str = validated_params.get("user", "")
    user_data = json.loads(user_data_str) if user_data_str else {}

    user_data["telegram_id"] = user_data.pop("id")
    user_data["role_id"] = role.id  # Assign the role ID to user_data

    existing_user = await get_user_by_tID(db, user_data.get("telegram_id"))
    if existing_user:
        return {
            "message": "Prevent multiple user creation, user already exists",
            "user": existing_user,
        }

    new_user = await create_user(db, UserCreate(**user_data))
    await assign_initial_quests(db, new_user.id)
    await assign_initial_achievements(db, new_user.id)

    new_user_with_assigned_data = await get_user_by_tID(
        db, user_data.get("telegram_id")
    )

    return {
        "message": "User created successfully with selected role.",
        "user": new_user_with_assigned_data,
    }


# Endpoint to delete a user by ID
@router.delete("/users/{user_id}")
@role_required(
    ["admin", "kingdom", "adventurer"]
)  # Only admin and kingdom can delete users
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
@role_required(["admin"])  # Only admin  can change users
async def update_all_information(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Change all information in selected user by their ID.

    - **user_id**: The ID of the user to put information.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user information changed, or raises a 404 error if not found.
    """
    query = select(UserModel).where(UserModel.telegram_id == user_id)
    query_result = await db.execute(query)
    user_info = query_result.scalar_one_or_none()

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

    # Сохраняем изменения в базе данных

    await db.commit()

    return {"message": "User information successfully replaced", "user": user_info}


@router.patch("/users/{user_id}")
@role_required(["admin"])  # Only admin  can change users
async def update_selected_information(
    user_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Change some selected information in selected user by their ID.

    - **user_id**: The ID of the user based on TG-ID.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user selected information changed, or raises a 404 error if not found.
    """
    query = select(UserModel).where(UserModel.telegram_id == user_id)
    query_result = await db.execute(query)
    user_info = query_result.scalar_one_or_none()

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

    # Сохраняем изменения в базе данных

    await db.commit()

    return {"message": "User information successfully replaced", "user": user_info}


@router.post("/users/{user_id}/quests/{quest_id}/complete")
async def complete_quest(
    user_id: UUID, quest_id: UUID, db: AsyncSession = Depends(get_db)
):
    return await complete_quest_and_take_rewards(user_id, quest_id, db)
