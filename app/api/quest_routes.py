# app/api/quest_routes.py
from sqlalchemy import select, update
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
    Body,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Reward as RewardModel, Quest, UserQuestProgress
from app.schemas import (
    Quest as QuestSchema,
    QuestBase,
    QuestsResponse,
    QuestPatchUpdate,
    RewardBase as RewardBaseSchema,
    InitialQuestResponse,
    QuestCreateResponse,
    User,
    UserQuestProgressResponse,
    UserQuestProgressChangesRequest,
    UserQuestProgress as UserQuestProgressSchema,
)
from app.crud import (
    create_quest,
    get_quests,
    get_quest_by_id,
    get_reward_by_quest_id,
    create_reward,
    delete_reward_by_id,
    create_quest,
    get_quests,
    get_quest_by_id,
    update_quest_fields_in_db,
    update_quest_in_db,
    delete_quest_in_db,
)
from app.database import get_db
from uuid import UUID
from app.utils.get_current_user import get_current_user
from app.utils.get_user_id import get_user_id
from datetime import datetime, timezone
from typing import Dict, List


from app.utils.role_check import role_required
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
@router.post("/quests", response_model=QuestCreateResponse, status_code=201)
async def create_new_quest(quest: QuestBase, db: AsyncSession = Depends(get_db)):
    """
    Create a new quest in the database.

    - **quest**: The quest data to be created, provided in the request body. Validated by Pydantic model QuestBase.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the created quest with its ID.
    """

    created_quest = await create_quest(quest, db)
    return created_quest


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


# @router.get("/quests/progress", response_model=Dict[str, UserQuestProgressResponse])
# async def get_user_quests(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(UserQuestProgress))
#     user_quest_records = result.scalars().all()

#     if not user_quest_records:
#         raise HTTPException(status_code=404, detail="No quest progress records found")

#     # Convert the list of `UserQuestProgress` objects to a dictionary keyed by quest ID
#     user_quest_dict = {
#         str(record.quest_id): UserQuestProgressResponse(
#             id=record.id,
#             userId=record.user_id,
#             questId=str(record.quest_id),
#             status=record.status,
#             progress=record.progress,
#             startedAt=record.started_at.isoformat() if record.started_at else None,
#             completedAt=(
#                 record.completed_at.isoformat() if record.completed_at else None
#             ),
#             mentorComment=record.mentor_comment,
#         )
#         for record in user_quest_records
#     }

#     return user_quest_dict


# @router.get("/quests/quests_progress")
@router.get(
    "/quests/quests_progress",
)
async def accept_quest(
    user_id: User = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Check if the quest exists
    result = await db.execute(
        select(UserQuestProgress).where(UserQuestProgress.user_id == user_id)
    )
    quests_progress = result.scalars().all()

    if not quests_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quests progress not found"
        )

    # Create a dictionary where id is the key and UserQuestProgressResponse is the value
    mapped_data = {quest.quest_id: quest for quest in quests_progress}

    return mapped_data


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


@router.get("/quests/{quest_id}/rewards")
async def get_quest_rewards(quest_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a rewards by quest ID from the database.

    - **quest_id**: The ID of the quest to retrieve.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a JSON object representing the quest. If the quest is not found, raises a 404 error.
    """

    reward = await get_reward_by_quest_id(quest_id, db)

    if reward is None:
        raise HTTPException(status_code=404, detail="Rewards not found")

    return reward


@router.post("/quests/{quest_id}/rewards")
async def create_for_quest_reward(
    quest_id: UUID, reward_data: RewardBaseSchema, db: AsyncSession = Depends(get_db)
):
    """
    Create a new reward  in the database with selected quest_id.

    - **quest**: The quest data to be created, provided in the request body.
    - **reward_data**: The reward data to be added to the reward table.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the created reward  with its ID.
    """
    return await create_reward(quest_id, reward_data, db)


@router.patch("/quests/{quest_id}/rewards/{reward_id}")
async def patch_the_reward(
    reward_id: UUID, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Update exist  reward  in the database.

    - **quest_id**: The quest data to be created, provided in the request body.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns the updated  reward.
    """
    query = select(RewardModel).where(RewardModel.id == reward_id)

    response = await db.execute(query)

    reward = response.scalar_one_or_none()
    new_request_data = await request.json()

    if not reward:
        raise HTTPException(
            status_code=404, detail="Reward does not exist for this quest"
        )

    available_fields = ["description", "coins", "points", "level_increase", "quest_id"]

    for field in available_fields:
        if field in new_request_data:
            setattr(reward, field, new_request_data[field])

    await db.commit()

    return {"message": "Reward  information successfully updated", "reward": reward}


@router.delete("/quests/{quest_id}/rewards/{reward_id}")
# @role_required(
#     ["admin", "kingdom", "adventurer"]
# )  # Only admin and kingdom can delete users ,,, With active required_role reward doesn't delete.
async def delete_reward(reward_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a reward  by reward ID.

    - **reward_id**: The ID of the user to delete.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Returns a success message if the user is deleted, or raises a 404 error if not found.
    """

    reward_deleted = await delete_reward_by_id(reward_id, db)
    if reward_deleted:
        return {"message": "Reward deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Reward not found")


# Endpoint for update quest completely
@router.put("/quests/{quest_id}", response_model=QuestSchema)
async def update_quest(
    quest_id: UUID, quest: QuestBase, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing quest completely in the database.

    - **quest_id**: The unique ID of the quest to update.
    - **quest**: The full quest data to replace the existing one, provided in the request body.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Raises a 404 error if the quest with the given ID is not found.
    Raises a 400 error if any required fields (name, image_url, description, requirements, award, goal) are missing.

    Returns the fully updated quest as a response model.
    """
    existing_quest = await get_quest_by_id(db, quest_id)
    if not existing_quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    updated_quest = await update_quest_in_db(db, existing_quest, quest)
    return updated_quest


# Endpoint for partially update quest
@router.patch("/quests/{quest_id}", response_model=QuestSchema)
async def partial_update_quest(
    quest_id: UUID, quest: QuestPatchUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Partially update an existing quest in the database.

    - **quest_id**: The unique ID of the quest to update.
    - **quest**: The fields of the quest to update, provided in the request body. Only fields with values will be updated.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Raises a 404 error if the quest with the given ID is not found.

    Returns the updated quest with only the modified fields.
    """
    existing_quest = await get_quest_by_id(db, quest_id)
    if not existing_quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    updated_fields = quest.dict(exclude_unset=True)  # Use Pydantic's exclude_unset
    updated_quest = await update_quest_fields_in_db(db, existing_quest, updated_fields)

    return updated_quest


# Endpoint for deleter quest
@router.delete("/quests/{quest_id}", status_code=204)
async def delete_quest(quest_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete an existing quest from the database.

    - **quest_id**: The unique ID of the quest to delete.
    - **db**: Database session dependency, automatically provided by FastAPI.

    Raises a 404 error if the quest with the given ID is not found.

    Returns a 204 status code with no content upon successful deletion.
    """
    quest = await get_quest_by_id(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    await delete_quest_in_db(db, quest)

    # Explicitly return a 204 No Content response
    return Response(status_code=204)


# Endpoint 1: Accept a Quest
# @router.post("/quests/{quest_id}/accept")
@router.post("/quests/{quest_id}/accept", response_model=UserQuestProgressResponse)
async def accept_quest(
    quest_id: UUID,
    user_id: User = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Check if the quest exists
    result = await db.execute(select(Quest).filter(Quest.id == quest_id))
    quest = result.scalar_one_or_none()
    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found"
        )

    # Check if the user has already accepted this quest
    result = await db.execute(
        select(UserQuestProgress).filter(
            UserQuestProgress.user_id == user_id,
            UserQuestProgress.quest_id == quest_id,
        )
    )
    existing_progress = result.scalar_one_or_none()

    if existing_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already accepted this quest",
        )

    # Create a new UserQuestProgress record
    new_progress = UserQuestProgress(
        user_id=user_id,
        quest_id=quest_id,
        status="IN_PROGRESS",  # Set initial quest status
    )

    # Add and commit the new progress
    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)

    return new_progress


# Endpoint 2: Submit a Quest for Review
@router.post("/quests/{quest_id}/submit", response_model=UserQuestProgressResponse)
async def submit_quest(
    quest_id: UUID,
    user_id: UUID = Depends(
        get_user_id
    ),  # Uses get_user_id to retrieve only the user's ID
    db: AsyncSession = Depends(get_db),
):
    # Check if the quest progress record exists for the user
    result = await db.execute(
        select(UserQuestProgress).filter(
            UserQuestProgress.user_id == user_id, UserQuestProgress.quest_id == quest_id
        )
    )
    quest_progress = result.scalars().first()

    # If no progress record, return an error
    if not quest_progress:
        raise HTTPException(
            status_code=404, detail="Quest progress not found for this user"
        )

    # Check if the quest is already in review or completed
    if quest_progress.status in ["REVIEW_PENDING", "TASK_COMPLETED"]:
        raise HTTPException(
            status_code=400,
            detail="Quest is already submitted for review or completed",
        )

    # Update quest status to "REVIEW_PENDING"
    quest_progress.status = "REVIEW_PENDING"
    # quest_progress.updated_at = datetime.now(timezone.utc)

    db.add(quest_progress)
    await db.commit()
    await db.refresh(quest_progress)

    return quest_progress


@router.post(
    "/quests/{quest_id}/request_changes", response_model=UserQuestProgressResponse
)
async def request_changes(
    quest_id: UUID,
    mentor_comment: UserQuestProgressChangesRequest,
    user_id: UUID = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserQuestProgress).filter(
            UserQuestProgress.user_id == user_id, UserQuestProgress.quest_id == quest_id
        )
    )
    quest_progress = result.scalars().first()

    if not quest_progress or quest_progress.status != "REVIEW_PENDING":
        raise HTTPException(
            status_code=400,
            detail="Quest is not in a reviewable state for requesting changes",
        )

    quest_progress.status = "CHANGES_REQUESTED"
    quest_progress.mentor_comment = mentor_comment.mentor_comment
    # quest_progress.updated_at = datetime.now(timezone.utc)

    db.add(quest_progress)
    await db.commit()
    await db.refresh(quest_progress)

    return quest_progress


@router.post("/quests/{quest_id}/complete", response_model=UserQuestProgressResponse)
async def complete_quest(
    quest_id: UUID,
    user_id: UUID = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserQuestProgress).filter(
            UserQuestProgress.user_id == user_id, UserQuestProgress.quest_id == quest_id
        )
    )
    quest_progress = result.scalars().first()

    if not quest_progress or quest_progress.status != "REVIEW_PENDING":
        raise HTTPException(
            status_code=400,
            detail="Quest is not in a reviewable state for completion",
        )

    quest_progress.status = "TASK_COMPLETED"
    # quest_progress.completed_at = datetime.now(timezone.utc)

    db.add(quest_progress)
    await db.commit()
    await db.refresh(quest_progress)

    return quest_progress


@router.post(
    "/quests/{quest_id}/accept_reward", response_model=UserQuestProgressResponse
)
async def complete_quest(
    quest_id: UUID,
    user_id: UUID = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserQuestProgress).filter(
            UserQuestProgress.user_id == user_id, UserQuestProgress.quest_id == quest_id
        )
    )
    quest_progress = result.scalars().first()

    if not quest_progress or quest_progress.status != "TASK_COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Quest is not in a accept reward state",
        )

    quest_progress.is_reward_accepted = True
    # quest_progress.completed_at = datetime.now(timezone.utc)

    db.add(quest_progress)
    await db.commit()
    await db.refresh(quest_progress)

    return quest_progress
