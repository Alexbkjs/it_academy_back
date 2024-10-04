# app/api/quest_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Quest as QuestSchema, QuestsResponse, InitialQuestResponse
from app.crud import create_quest, get_quests, get_quest_by_id
from app.database import get_db
from uuid import UUID
from app.utils.get_current_user import get_current_user

from app.crud import get_initial_quest

# Create an APIRouter instance for quest-related routes

router = APIRouter()


@router.get(
    "/quests/initial-quest",
    response_model=QuestSchema,  # Specify the response model
)
async def read_initial_quest(db: AsyncSession = Depends(get_db)):
    """
    Fetch the initial quest for new users asynchronously.

    This endpoint retrieves the initial quest that new users must complete.
    If the quest is not found, it raises a 404 HTTP exception.

    Args:
        db (AsyncSession, optional): The database session injected via
        dependency injection.

    Raises:
        HTTPException: Raises a 404 error if the initial quest is not found.

    Returns:
        Quest: The initial quest object to be returned in the response.
    """
    # Await the asynchronous function to fetch the initial quest
    quest = await get_initial_quest(db)

    if not quest:
        # Raise a 404 error if the initial quest is not found
        raise HTTPException(status_code=404, detail="Initial quest not found")

    return quest


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
    return QuestsResponse(
        message="List of quests fetched from the database.",
        quests=quests,
        total=total_count,
    )


@router.get("/quests/{quest_id}", response_model=QuestSchema)
async def read_quest(
    quest_id: UUID,  # The ID of the quest to retrieve
    db: AsyncSession = Depends(get_db),  # Dependency injection for the database session
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
