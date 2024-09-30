from fastapi import (
    APIRouter,
    Depends,
    Request,
)  # FastAPI components for routing and error handling
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)  # SQLAlchemy for asynchronous database operations
from app.database import get_db
from app.crud import get_data_leaderboard
import json

router = APIRouter()  # Create an APIRouter instance for handling routes


@router.get("/leaderboard")
async def get_leaderboard(request: Request, db: AsyncSession = Depends(get_db)):
    query_params = request.query_params
    time_type = query_params.get("timeType")
    time_count = int(query_params.get("timeCount", 1))

    period = {"day": 1, "week": 7, "month": 30, "allTime": 365}
    limit = period.get(time_type, 0) * time_count

    validated_params = request.state.validated_params
    user_data_str = validated_params.get("user", "")
    user_data = json.loads(user_data_str) if user_data_str else {}
    telegram_id = user_data["id"]

    leaderboard_data = await get_data_leaderboard(telegram_id, limit, db)

    return leaderboard_data
