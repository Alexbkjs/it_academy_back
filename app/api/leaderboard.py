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
    validated_params = request.state.validated_params
    user_data_str = validated_params.get("user", "")
    user_data = json.loads(user_data_str) if user_data_str else {}
    telegram_id = user_data["id"]

    leaderboard_data = {
        "7days": await get_data_leaderboard(telegram_id, 7, db),
        "30days": await get_data_leaderboard(telegram_id, 30, db),
        "6months": await get_data_leaderboard(telegram_id, 180, db),
    }

    return leaderboard_data
