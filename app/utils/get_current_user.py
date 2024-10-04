import json
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.database import get_db


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    validated_params = getattr(request.state, "validated_params", None)

    if validated_params is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse the 'user' field
    user_data = validated_params.get("user")
    if user_data is None:
        raise HTTPException(
            status_code=401,
            detail="User data missing from request",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_data = json.loads(user_data)
        user_id = user_data.get("id")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user data format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing from user data",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user asynchronously
    result = await db.execute(select(User).filter(User.telegram_id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
