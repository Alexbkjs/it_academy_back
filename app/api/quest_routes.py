# app/api/quest_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Quest as QuestSchema
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
@router.get("/quests/")
async def read_quests(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10
):
    """
    Retrieve a list of quests from the database.

    - **db**: Database session dependency, automatically provided by FastAPI.
    - **skip**: Number of quests to skip (for pagination).
    - **limit**: Maximum number of quests to return.

    Returns a JSON object with a list of quests under the 'quests' key.
    """
    quests_data = await get_quests(db, skip, limit)

    # Directly constructing the response with camelCase keys
    transformed_quests = [
        {
            "id": str(quest.id),
            "name": quest.name,
            "description": quest.description,
            "goal": quest.goal,
            "award": quest.award,
            "imageUrl": quest.image_url,
            "createdAt": quest.created_at,
            "updatedAt": quest.updated_at,
        }
        for quest in quests_data
    ]

    return {"quests": transformed_quests}


@router.get("/quests/{quest_id}")
async def read_quest(quest_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single quest by its ID from the database.

    - **quest_id**: The ID of the quest to retrieve.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a JSON object representing the quest.
    """
    quest_data = await get_quest_by_id(db, quest_id)

    if quest_data is None:
        raise HTTPException(status_code=404, detail="Quest not found")

    # Transform the quest data to a dictionary with camelCase keys
    transformed_quest = {
        "id": str(quest_data.id),
        "name": quest_data.name,
        "description": quest_data.description,
        "goal": quest_data.goal,
        "award": quest_data.award,
        "requirements": quest_data.requirements,
        "imageUrl": quest_data.image_url,  # CamelCase key
        "createdAt": (
            quest_data.created_at.isoformat() if quest_data.created_at else None
        ),
        "updatedAt": (
            quest_data.updated_at.isoformat() if quest_data.updated_at else None
        ),
    }

    return transformed_quest
