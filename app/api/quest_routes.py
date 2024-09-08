# app/api/quest_routes.py

from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Quest
from app.crud import create_quest, get_quests
from app.database import get_db

# Create an APIRouter instance for quest-related routes
router = APIRouter()

# Endpoint to create a new quest
@router.post("/quests/", response_model=Quest)
async def create_new_quest(quest: Quest, db: AsyncSession = Depends(get_db)):
    """
    Create a new quest in the database.
    
    - **quest**: The quest data to be created, provided in the request body.
    - **db**: Database session dependency, automatically provided by FastAPI.
    
    Returns the created quest with its ID.
    """
    return await create_quest(quest, db)

# Endpoint to retrieve a list of quests with optional pagination
@router.get("/quests/", response_model=List[Quest])
async def read_quests(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    Retrieve a list of quests from the database.
    
    - **db**: Database session dependency, automatically provided by FastAPI.
    - **skip**: Number of quests to skip (for pagination).
    - **limit**: Maximum number of quests to return.
    
    Returns a list of quests.
    """
    return await get_quests(db, skip, limit)
 
