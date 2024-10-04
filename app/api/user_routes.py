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
from sqlalchemy.future import select

# Local Application Imports
from app.schemas import (
    UserBase as User,
    UserResponse,
    UserRoleCreate,
    UserCreate,
    UpdateUserClassRequest,
)  # User data validation schema
from app.crud import (
    get_user_by_tID,
    create_user,
    delete_user_by_id,
    assign_initial_quests,
    assign_initial_achievements,
)  # CRUD operations
from app.database import get_db  # Database session dependency
from app.models import UserRoleModel
from app.utils.get_current_user import get_current_user

from app.utils.role_check import role_required
from app.models import User as UserModel

router = APIRouter()  # Create an APIRouter instance for handling routes


# @router.put("/user/class", response_model=UserResponse) // getting validation error
@router.put("/user/class")
async def update_user_class(
    update_data: UpdateUserClassRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate user class
    if update_data.userClass not in ["frontend", "designer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user class. Choose either 'frontend' or 'designer'.",
        )

    # Update the user class directly
    current_user.user_class = update_data.userClass

    # Commit the change
    await db.commit()
    await db.refresh(current_user)

    # Return the updated user
    return {
        "message": "User was updated successfully",
        "user": current_user,  # Convert to Pydantic model
    }


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


@router.post("/user", response_model=UserResponse)
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
@router.delete("/user/{user_id}")
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
