# app/api/quest_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Quest as QuestSchema, QuestsResponse
from app.crud import create_quest, get_quests, get_quest_by_id
from app.database import get_db
from uuid import UUID


# Create an APIRouter instance for quest-related routes
router = APIRouter()


# Endpoint to create a new quest
@router.post("/quests/", response_model=QuestSchema)
async def create_new_quest(quest: QuestSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new quest in the database.

    - **quest**: The quest data to be created, provided in the request body.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the created quest with its ID.
    """
    return await create_quest(quest, db)


# Endpoint to retrieve a list of quests with optional pagination
@router.get("/quests", response_model=QuestsResponse)
async def read_quests(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10
):
    """
    Retrieve a list of quests from the database.

    - **db**: Database session dependency, automatically provided by FastAPI.
    - **skip**: Number of quests to skip (for pagination).
    - **limit**: Maximum number of quests to return.

    Returns a JSON object with a list of quests under the 'quests' key in camelCase format.
    The quests are returned as a list of `QuestBase` objects.
    """
    # Fetch quests from the database along with the total count for pagination
    quests, total_count = await get_quests(db, skip, limit)
    
    # Return a response model containing the list of quests and the total count
    return QuestsResponse(quests=quests, total=total_count)



# @router.get("/quests/{quest_id}", response_model=QuestSchema)
# async def read_quest(quest_id: UUID, db: AsyncSession = Depends(get_db)):
#     """
#     Retrieve a single quest by its ID from the database.

#     - **quest_id**: The ID of the quest to retrieve.
#     - **db**: Database session dependency, automatically provided by FastAPI.

#     Returns a JSON object representing the quest.
#     """
#     quest = await get_quest_by_id(db, quest_id)
#     if quest is None:
#         raise HTTPException(status_code=404, detail="Quest not found")

#     return quest


@router.get("/quests/{quest_id}", response_model=QuestSchema)
async def read_quest(
    quest_id: UUID,  # The ID of the quest to retrieve
    db: AsyncSession = Depends(get_db)  # Dependency injection for the database session
):
    """
    Retrieve a single quest by its ID from the database.

    - **quest_id**: The ID of the quest to retrieve.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a JSON object representing the quest. If the quest is not found, raises a 404 error.
    """
    # Fetch the quest from the database using the provided quest_id
    quest = await get_quest_by_id(db, quest_id)

    # Check if the quest was found; if not, raise a 404 error
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")

    # Return the retrieved quest as a QuestSchema
    return quest