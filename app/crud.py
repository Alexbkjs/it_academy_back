from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import func

from app.models import (
    User as UserModel,
    Quest as QuestModel,
    UserQuestProgress as UserQuestProgressModel,
    Achievement as AchievementModel,
    UserAchievementModel,
)
from app.schemas import User as UserSchema, Quest as QuestSchema
from app.utils.photo_users import get_user_profile_photo_link
from uuid import UUID

from sqlalchemy.orm import (
    selectinload,
    joinedload,
)  # Import selectinload for eager loading of related rows


# Function to delete a user by their ID (Telegram_id) in a cascade manner


async def delete_user_by_id(db: AsyncSession, user_id: int):
    # Create a select query to find a user with the given ID and load related entities if necessary
    query = (
        select(UserModel)
        .filter_by(telegram_id=user_id)
        .options(
            selectinload(UserModel.quest_progress), selectinload(UserModel.achievements)
        )
    )
    result = await db.execute(query)  # Execute the query asynchronously
    user = (
        result.scalar_one_or_none()
    )  # Get the single result (or None if no user found)

    # If a user is found, delete it and commit the transaction
    if user:
        await db.delete(user)
        await db.commit()
        return True  # Return True if the deletion was successful
    return False  # Return False if no user was found


async def create_user(db: AsyncSession, user: UserSchema) -> UserModel:
    """
    Create a new user in the database.

    - **db**: Database session dependency.
    - **user**: Pydantic model containing user data.

    Returns the created user instance.
    """
    image_url = await get_user_profile_photo_link(
        user.telegram_id
    )  # get link user photo
    # Create a new User model instance, including the selected role

    new_user = UserModel(**user.dict())  # Unpack user data into UserModel
    # Add the new User instance to the session
    db.add(new_user)

    # Commit the transaction to persist the new User instance
    await db.commit()

    # Refresh the instance to load any database-generated fields like 'id'
    await db.refresh(new_user)
    return new_user


async def get_user_by_tID(db: AsyncSession, telegram_id: int):
    # Create a select query to find a user with the given telegram_id and load related quest progress and quests
    query = (
        select(UserModel)
        .where(UserModel.telegram_id == telegram_id)
        .options(
            joinedload(UserModel.quest_progress).joinedload(
                UserQuestProgressModel.quest
            ),
            joinedload(UserModel.achievements).joinedload(
                UserAchievementModel.achievement
            ),  # Load the Achievement through UserAchievementModel
        )
    )

    result = await db.execute(query)  # Execute the query asynchronously
    user = result.scalars().first()  # Get the first result (or None if no user found)

    # Convert the SQLAlchemy model instance to a dictionary before validating
    if user:
        user_dict = vars(user)  # Get user fields without internal SQLAlchemy stuff

        # Access and reverse the quest_progress list
        if "quest_progress" in user_dict and user_dict["quest_progress"]:
            quest_progress = user_dict["quest_progress"]

            # Reverse the list without modifying the original (if immutability is needed)
            quest_progress_reversed = quest_progress[::-1]

            # Update the quest_progress field with the reversed list
            user_dict["quest_progress"] = quest_progress_reversed

        # Return the user as a UserSchema with loaded quests if found, otherwise None
        return UserSchema.model_validate(user_dict) if user_dict else None


# Function to create a new quest in the database
async def create_quest(quest: QuestSchema, db: AsyncSession):
    # Create an insert query for the QuestModel table with the provided quest data
    query = QuestModel.__table__.insert().values(
        title=quest.title, description=quest.description
    )
    result = await db.execute(query)  # Execute the query asynchronously
    await db.commit()  # Commit the transaction
    # Return the quest data with the newly inserted ID
    return {**quest.model_dump(), "id": result.inserted_primary_key[0]}


# Function to retrieve a list of quests with optional pagination
async def get_quests(db: AsyncSession, skip: int = 0, limit: int = 10):
    # Create a query to select quests with pagination using offset and limit
    query = select(QuestModel).offset(skip).limit(limit)

    # Execute the query asynchronously and get the result
    result = await db.execute(query)

    # Extract the list of quests from the result
    quests = result.scalars().all()

    # Create a separate query to count the total number of quests in the database
    total_count = await db.execute(select(func.count()).select_from(QuestModel))

    # Map the SQLAlchemy quest objects to Pydantic models and return them along with the total count
    return [QuestSchema.from_orm(quest) for quest in quests], total_count.scalar()


# Function to retrieve one quest by ID
async def get_quest_by_id(db: AsyncSession, quest_id: UUID):
    result = await db.execute(select(QuestModel).where(QuestModel.id == quest_id))
    return QuestSchema.from_orm(
        result.scalar_one_or_none()
    )  # Returns the quest or None if not found


async def assign_initial_quests(db: AsyncSession, user_id: UUID):
    """
    Assign 4 quests to a new user, with 2 being blocked and 2 being active.

    - **db**: Database session dependency.
    - **user_id**: ID of the newly created user.
    """

    # Fetch quests from the database (modify as needed to suit your schema and requirements)
    result = await db.execute(
        select(QuestModel).limit(4)  # Fetching 4 quests; adjust as needed
    )
    quests = result.scalars().all()

    if len(quests) < 4:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not enough quests available to assign.",
        )

    # Assign quests, with 2 blocked and 2 not blocked
    for idx, quest in enumerate(quests):
        quest_status = "blocked" if idx >= 2 else "active"
        await db.execute(
            UserQuestProgressModel.__table__.insert().values(
                user_id=user_id,
                quest_id=quest.id,
                status=quest_status,
                is_locked=quest_status
                == "blocked",  # Using is_locked to reflect blocked status
            )
        )

    await db.commit()


async def assign_initial_achievements(db: AsyncSession, user_id: UUID):
    """
    Assign specific achievements to a new user, such as basic achievements for registration.

    - **db**: Database session dependency.
    - **user_id**: ID of the newly created user.
    """

    # Predefine the list of specific achievements (e.g., by achievement name or type)
    achievement_names = ["Початківець", "Новачок", "Дослідник", "Воїн"]

    # Fetch the specific achievements from the database
    result = await db.execute(
        select(AchievementModel).where(AchievementModel.name.in_(achievement_names))
    )
    achievements = result.scalars().all()

    if len(achievements) < 4:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not enough specific achievements available to assign.",
        )
    # Assign achievements, with 2 active and 2 blocked
    for idx, achievement in enumerate(achievements):
        achievement_status = "blocked" if idx >= 2 else "active"
        is_locked = False if achievement_status == "active" else True
        await db.execute(
            UserAchievementModel.__table__.insert().values(
                user_id=user_id,
                achievement_id=achievement.id,
                status=achievement_status,
                is_locked=is_locked,
            )
        )

    await db.commit()


async def get_data_leaderboard(telegram_id: int, days: int, db: AsyncSession):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    # Query to select the top users ordered by points in descending order within the time frame
    query_top = (
        select(UserModel)
        .where(UserModel.updated_at >= cutoff_date)
        .order_by(desc(UserModel.points))
    )
    # Query to select the specific user based on telegram_id
    query_user = select(UserModel).order_by(desc(UserModel.points))
    result_top = await db.execute(
        query_top
    )  # Execute the top users query asynchronously
    result_user = await db.execute(query_user)  # Execute the user query asynchronously

    all_users = result_top.scalars().all()
    user_info = result_user.scalars().all()
    users_list = []
    current_user = None
    for index, user in enumerate(all_users):
        if index == days:
            break
        user_data = {
            "id": str(user.id),
            "telegramId": str(user.telegram_id),
            "firstName": user.first_name,
            "lastName": user.last_name,
            "imageUrl": user.image_url,
            "points": user.points,
            "position": index + 1,
            "isCurrentUser": user.telegram_id == telegram_id,
        }
        users_list.append(user_data)
        if index == days:
            break

    for index, user in enumerate(user_info):
        if user.telegram_id == telegram_id:
            current_user = {
                "id": str(user.id),
                "telegramId": str(user.telegram_id),
                "firstName": user.first_name,
                "lastName": user.last_name,
                "imageUrl": user.image_url,
                "points": user.points,
                "position": index + 1,
                "isCurrentUser": True,
            }
            break

    return {
        "users": users_list,
        "currentUser": current_user,
    }
