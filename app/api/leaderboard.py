from fastapi import APIRouter, Depends, Request, status  # FastAPI components for routing and error handling
from sqlalchemy.ext.asyncio import AsyncSession  # SQLAlchemy for asynchronous database operations
from app.database import get_db
from app.crud import get_data_leaderboard
from app.schemas import User as UserSchema
import json

router = APIRouter()  # Create an APIRouter instance for handling routes

# Endpoint to verify initial data and handle user authentication
@router.get("/leaderboard")
async def get_leaderboard(request: Request, db: AsyncSession = Depends(get_db)):

    validated_params = request.state.validated_params
    user_data_str = validated_params.get('user', '')
    user_data = json.loads(user_data_str) if user_data_str else {}
    telegram_id = user_data["id"]

    existing_lead = await get_data_leaderboard(telegram_id,5, db)
    user_data_response = []
    for user in existing_lead:
        UserSchema.model_validate(user) if user else None
        if user:
            user_data_response.append({
                "position": user['position'],
                "telegram_id": user['telegram_id'],
                "first_name": user['first_name'],
                "points": user['points'],
            })
    return {"user": user_data_response, "message": "leaderboard"}


