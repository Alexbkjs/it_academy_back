import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models import Base, User, Quest, Achievement, UserQuestProgress, Requirement, Reward, UserRole

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# To ensure that the Requirement, Reward, and UserQuestProgress records correctly reference existing Quest and User records,
# you need to first fetch the created records and use their UUIDs for foreign key relationships. Here’s how you can modify your 
# code to handle these dependencies correctly:

# Create an async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Async function to create the tables
async def create_tables():
    async with async_engine.begin() as conn:
        # Drop all tables (for development/testing purposes, remove in production)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def seed_users():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            users = [
                User(
                    id=uuid.uuid4(), 
                    telegram_id=123456789, 
                    first_name="John", 
                    last_name="Doe", 
                    username="john_doe", 
                    user_class="Warrior", 
                    role=UserRole.adventurer, 
                    level=1, 
                    points=222, 
                    coins=3333, 
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/02.jpg", 
                    language_code="en",
                    allows_write_to_pm=True
                ),
                User(
                    id=uuid.uuid4(), 
                    telegram_id=987654321, 
                    first_name="Jane", 
                    last_name="Doe", 
                    username="jane_doe", 
                    user_class="Mage", 
                    role=UserRole.avatar, 
                    level=2, 
                    points=444, 
                    coins=5555, 
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/02.jpg", 
                    language_code="en",
                    allows_write_to_pm=True
                ),
            ]
            session.add_all(users)
        await session.commit()

async def seed_quests():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            quests = [
                Quest(id=uuid.uuid4(), name="Базовий квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/basic.png", description="Візит до Академії для отримання першого рівня та вибору базового класу", award="очки досвіду, підвищення класу", goal="Візит до Академії для отримання першого рівня та вибору базового класу"),
                Quest(id=uuid.uuid4(), name="Рутинний квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/routine.png", description="Виконання тестового завдання для отримання артефакту та Мідних Монет", award="очки досвіду, мідні монети, артефакти", goal="Виконання тестового завдання для отримання артефакту та Мідних Монет"),
                Quest(id=uuid.uuid4(), name="Пригодницький квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/adventure.png", description="Проходження кар’єрного коучинга, навчальних курсів та подібних завдань", award="підвищення класу, рівня, артефакти, мідні монети", goal="Проходження кар’єрного коучинга, навчальних курсів та подібних завдань"),
                Quest(id=uuid.uuid4(), name="Багаторазовий квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/reusable.png", description="Залучайте нових учасників за партнерським посиланням", award="очки досвіду", goal="Залучайте нових учасників за партнерським посиланням"),
                Quest(id=uuid.uuid4(), name="Командний квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/team.png", description="Участь у командному проекті для отримання досвіду та Золотих Монет", award="очки досвіду, золоті та мідні монети, артефакти", goal="Участь у командному проекті для отримання досвіду та Золотих Монет"),
                Quest(id=uuid.uuid4(), name="Битва з міні-босом", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/mini_boss.png", description="Складання онлайн-іспиту для отримання артефакту", award="артефакти", goal="Складання онлайн-іспиту для отримання артефакту"),
            ]
            session.add_all(quests)
        await session.commit()

async def seed_achievements():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            achievements = [
                Achievement(id=uuid.uuid4(), name="Початківець", description="Отримати перший рівень", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_1.png"),
                Achievement(id=uuid.uuid4(), name="Новачок", description="Завершити базове навчання", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_2.png"),
                Achievement(id=uuid.uuid4(), name="Дослідник", description="Виконати 3 різні квести", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_3.png"),
                Achievement(id=uuid.uuid4(), name="Воїн", description="Здобути 5 артефактів", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_4.png"),
                Achievement(id=uuid.uuid4(), name="Командир", description="Завершити командний квест", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_5.png"),
                Achievement(id=uuid.uuid4(), name="Маг", description="Досягнути 10-го рівня", image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_6.png"),
            ]
            session.add_all(achievements)
        await session.commit()

async def seed_requirements():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch existing quests
            result = await session.execute(select(Quest))
            quests = result.scalars().all()

            # Ensure there are quests to reference
            if not quests:
                raise RuntimeError("No quests available to reference in requirements")

            requirements = [
                Requirement(id=uuid.uuid4(), description="Завершити перший рівень", quest_id=quests[0].id),
                Requirement(id=uuid.uuid4(), description="Завершити другий рівень", quest_id=quests[1].id),
                # Add more requirements as needed
            ]
            session.add_all(requirements)
        await session.commit()

async def seed_rewards():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch existing quests
            result = await session.execute(select(Quest))
            quests = result.scalars().all()

            # Ensure there are quests to reference
            if not quests:
                raise RuntimeError("No quests available to reference in rewards")

            rewards = [
                Reward(id=uuid.uuid4(), description="Артефакт першого рівня", quest_id=quests[0].id),
                Reward(id=uuid.uuid4(), description="Артефакт другого рівня", quest_id=quests[1].id),
                # Add more rewards as needed
            ]
            session.add_all(rewards)
        await session.commit()

async def seed_user_quest_progress():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetch existing users and quests
            result = await session.execute(select(User))
            users = result.scalars().all()

            result = await session.execute(select(Quest))
            quests = result.scalars().all()

            # Ensure there are users and quests to reference
            if not users:
                raise RuntimeError("No users available to assign quest progress")
            if len(quests) < 2:
                raise RuntimeError("Not enough quests available to assign to users")

            user_quest_progress = []
            for user in users:
                user_quest_progress.extend([
                    UserQuestProgress(id=uuid.uuid4(), user_id=user.id, quest_id=quests[0].id, status="in_progress", progress=50.0),
                    UserQuestProgress(id=uuid.uuid4(), user_id=user.id, quest_id=quests[1].id, status="in_progress", progress=75.0),
                ])
            session.add_all(user_quest_progress)
        await session.commit()

async def main():
    await create_tables()
    await seed_users()
    await seed_quests()
    await seed_achievements()
    await seed_requirements()
    await seed_rewards()
    await seed_user_quest_progress()

if __name__ == "__main__":
    asyncio.run(main())
