# Standard Library Imports
import json  # For JSON parsing

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

# Local Application Imports
from app.schemas import (
    UserBase,
    RoleSelection,
    UserResponse,
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
    role_selection: RoleSelection,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new user after role selection. Assigns initial quests and achievements
    if the user doesn't exist. Prevents multiple user creation if the user already exists.

    - **role_selection**: Contains the role selected by the user.
    - **request**: The HTTP request, used to access validated params.
    - **db**: AsyncSession for database operations.

    Returns the created or existing user along with a message.
    """
    # Retrieve validated params from the request state
    validated_params = request.state.validated_params
    # Extract the 'user' data as a string from validated params
    user_data_str = validated_params.get("user", "")
    # Parse the user data string into a dictionary if it exists, else use an empty dict
    user_data = json.loads(user_data_str) if user_data_str else {}

    # Replace 'id' with 'telegram_id' in user data to match the database field
    user_data["telegram_id"] = user_data.pop("id")
    # Assign the selected role to the user data
    user_data["role"] = role_selection.role

    # Check if a user with the provided Telegram ID already exists
    existing_user = await get_user_by_tID(db, user_data.get("telegram_id"))
    if existing_user:
        # If the user already exists, return a message and the user data
        return {
            "message": "Prevent multiple user creation, user already exists",
            "user": existing_user,
        }

    else:
        # If the user doesn't exist, create a new user using the provided data
        new_user = await create_user(db, UserBase(**user_data))

        # Assign initial quests and achievements to the newly created user
        await assign_initial_quests(db, new_user.id)
        await assign_initial_achievements(db, new_user.id)

        # Fetch the newly created user along with assigned data (quests, achievements)
        new_user_with_assigned_data = await get_user_by_tID(
            db, user_data.get("telegram_id")
        )

        # Return a success message along with the newly created user data
        return {
            "message": "User created successfully with selected role. Initial quests have been assigned.",
            "user": new_user_with_assigned_data,
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
