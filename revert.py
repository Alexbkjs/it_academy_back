import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import text
from app.models import User, Quest, Achievement, Requirement, Reward, UserQuestProgress

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def delete_users():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all users
            result = await session.execute(select(User))
            users = result.scalars().all()

            if users:
                user_ids = [str(user.id) for user in users]
                # Create a formatted list for SQL IN clause
                formatted_ids = ','.join(f"'{user_id}'" for user_id in user_ids)
                # Construct the query string
                query = f"DELETE FROM users WHERE id IN ({formatted_ids})"
                # Execute the query
                await session.execute(text(query))
                print(f"Deleted {len(users)} users.")
        await session.commit()

async def delete_quests():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all quests
            result = await session.execute(select(Quest))
            quests = result.scalars().all()

            if quests:
                quest_ids = [str(quest.id) for quest in quests]
                formatted_ids = ','.join(f"'{quest_id}'" for quest_id in quest_ids)
                query = f"DELETE FROM quests WHERE id IN ({formatted_ids})"
                await session.execute(text(query))
                print(f"Deleted {len(quests)} quests.")
        await session.commit()

async def delete_achievements():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all achievements
            result = await session.execute(select(Achievement))
            achievements = result.scalars().all()

            if achievements:
                achievement_ids = [str(achievement.id) for achievement in achievements]
                formatted_ids = ','.join(f"'{achievement_id}'" for achievement_id in achievement_ids)
                query = f"DELETE FROM achievements WHERE id IN ({formatted_ids})"
                await session.execute(text(query))
                print(f"Deleted {len(achievements)} achievements.")
        await session.commit()

async def delete_requirements():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all requirements
            result = await session.execute(select(Requirement))
            requirements = result.scalars().all()

            if requirements:
                requirement_ids = [str(requirement.id) for requirement in requirements]
                formatted_ids = ','.join(f"'{requirement_id}'" for requirement_id in requirement_ids)
                query = f"DELETE FROM requirements WHERE id IN ({formatted_ids})"
                await session.execute(text(query))
                print(f"Deleted {len(requirements)} requirements.")
        await session.commit()

async def delete_rewards():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all rewards
            result = await session.execute(select(Reward))
            rewards = result.scalars().all()

            if rewards:
                reward_ids = [str(reward.id) for reward in rewards]
                formatted_ids = ','.join(f"'{reward_id}'" for reward_id in reward_ids)
                query = f"DELETE FROM rewards WHERE id IN ({formatted_ids})"
                await session.execute(text(query))
                print(f"Deleted {len(rewards)} rewards.")
        await session.commit()

async def delete_user_quest_progress():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch all user quest progress
            result = await session.execute(select(UserQuestProgress))
            user_quest_progress = result.scalars().all()

            if user_quest_progress:
                up_ids = [str(up.id) for up in user_quest_progress]
                formatted_ids = ','.join(f"'{up_id}'" for up_id in up_ids)
                query = f"DELETE FROM user_quest_progress WHERE id IN ({formatted_ids})"
                await session.execute(text(query))
                print(f"Deleted {len(user_quest_progress)} user quest progress records.")
        await session.commit()

async def main():
    await delete_users()
    await delete_quests()
    await delete_achievements()
    await delete_requirements()
    await delete_rewards()
    await delete_user_quest_progress()

if __name__ == "__main__":
    asyncio.run(main())
