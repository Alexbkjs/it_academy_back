import json
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from uuid import UUID
from app.crud import get_user_by_tID


async def get_user_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    validated_params = getattr(request.state, "validated_params", None)

    if validated_params is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    # Parse the 'user' field
    user_data = validated_params.get("user")
    if user_data is None:
        raise HTTPException(
            status_code=401,
            detail="User data missing from request",
        )

    try:
        user_data = json.loads(user_data)
        user_id = user_data.get("id")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user data format",
        )

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing from user data",
        )

    user = await get_user_by_tID(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user.id
