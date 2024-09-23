from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import func


from app.models import (
    User as UserModel,
    Quest as QuestModel,
    UserQuestProgress as UserQuestProgressModel,
    Achievement as AchievementModel,
    UserAchievementModel,
)
from app.schemas import User as UserSchema, Quest as QuestSchema
from uuid import UUID

from sqlalchemy.future import select  # Import select for query building
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
    # Create a new User model instance, including the selected role
    new_user = UserModel(
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        is_premium=user.is_premium,
        allows_write_to_pm=user.allows_write_to_pm,
        role=user.role,  # Include the selected role
    )

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
    user_dict = user.__dict__ if user else None

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
    return QuestSchema.from_orm(result.scalar_one_or_none())  # Returns the quest or None if not found



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
        status = "blocked" if idx >= 2 else "active"
        await db.execute(
            UserQuestProgressModel.__table__.insert().values(
                user_id=user_id,
                quest_id=quest.id,
                status=status,
                is_locked=status
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
        status = "blocked" if idx >= 2 else "active"
        is_locked = False if status == "active" else True
        await db.execute(
            UserAchievementModel.__table__.insert().values(
                user_id=user_id,
                achievement_id=achievement.id,
                status=status,
                is_locked=is_locked,
            )
        )

    await db.commit()


async def get_data_leaderboard(telegram_id: int, limit_lead: int, db: AsyncSession):
    # Query to select the top "limit_lead" users ordered by their points in descending order
    query_top = select(UserModel).order_by(desc(UserModel.points))
    # Query to select the user based on telegram_id
    query_user = select(UserModel).where(UserModel.telegram_id == telegram_id)
    result_top = await db.execute(
        query_top
    )  # Execute the top users query asynchronously
    result_user = await db.execute(query_user)  # Execute the user query asynchronously
    all_users = result_top.scalars().all()
    for index, user in enumerate(all_users):
        if user.telegram_id == telegram_id:
            user_position: int = index + 1  # Позиції починаються з 1
            break

    # Create a list of top users' dictionaries from the result, or an empty list if no results
    users_list = (
        [
            {**row.__dict__, "position": index + 1}
            for index, row in enumerate(all_users)
        ][:limit_lead]
        if all_users
        else []
    )

    # Get the user information for the specified telegram_id, or None if not found
    user_info = result_user.scalars().first()

    if user_info:  # Check if the user exists in the database
        user_dict = {
            **user_info.__dict__,
            "position": user_position,
        }  # Convert user_info to dictionary format

        # Check if the user is already in the top users list
        if user_dict not in users_list:
            # If the user is not in the list and the list is already full ("limit_lead" users)
            if len(users_list) == limit_lead:
                users_list.pop()  # Remove the last user from the list to make space for a new one

            users_list.append(user_dict)  # Append the new user to the users list
    return users_list
