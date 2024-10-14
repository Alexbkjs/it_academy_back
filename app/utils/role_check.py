from typing import List
from functools import wraps

from fastapi import Request, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_user_by_tID
import json


def role_required(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            request: Request,
            db: AsyncSession = Depends(get_db),
            user_id: int = Path(...),
        ):
            # Retrieve the validated params stored in the request by the middleware
            user_data = request.state.validated_params.get("user")

            # Ensure user_data is a valid dictionary
            if isinstance(user_data, str):
                try:
                    user_data = json.loads(user_data)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400, detail="Invalid user data format"
                    )

            # Access the Telegram ID from user data
            telegram_id = user_data.get("id")
            if not telegram_id:
                raise HTTPException(status_code=403, detail="User ID not found")

            # Fetch the user role from the database using Telegram ID
            user_role = await get_user_role(db, telegram_id)
            if user_role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            # Proceed with the original function
            return await func(user_id=user_id, db=db, request=request)

        return wrapper

    return decorator


async def get_user_role(db: AsyncSession, telegram_id: int):
    """Fetch the user role based on the Telegram ID."""
    user = await get_user_by_tID(db, telegram_id)
    return user.role.role_name if user else None


# # Example usage in a route
# Apply role-based access control to the route

# @router.delete("/user/{user_id}")
# @role_required(["admin", "kingdom"])  # Only admin and kingdom can delete users
# async def delete_user(user_id: str):
#     # Logic for deleting the user
#     return {"message": "User deleted successfully"}
