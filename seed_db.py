import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models import (
    Base,
    User,
    Quest,
    Achievement,
    Reward,
    UserRoleModel,
)

import httpx
import random


from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load the DATABASE_URL from the .env files or from shell enviroment variables
# You can check it using this command "echo $DATABASE_URL"
# To set new: export DATABASE_URL="postgresql+asyncpg://admin:pass@it-academy-rpg-db.northeurope.azurecontainer.io:5432/iar_db"
DATABASE_URL = os.getenv("DATABASE_URL")

print("Working with db from: ", DATABASE_URL)


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


# Function to check if the database is empty
async def is_database_empty():
    async with AsyncSessionLocal() as session:
        # Check if any data exists in the User or Quest tables
        result = await session.execute(select(User).limit(1))
        user_exists = result.scalars().first()

        result = await session.execute(select(Quest).limit(1))
        quest_exists = result.scalars().first()

        # If both are empty, the database is considered empty
        return not user_exists and not quest_exists


# Async function to create the tables
async def create_tables():
    async with async_engine.begin() as conn:
        # Drop all tables (for development/testing purposes, remove in production)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def seed_roles():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if roles already exist
            existing_roles = await session.execute(
                select(UserRoleModel).where(
                    UserRoleModel.role_name.in_(
                        ["adventurer", "avatar", "kingdom", "admin"]
                    )
                )
            )
            existing_roles = existing_roles.scalars().all()
            existing_role_names = {role.role_name for role in existing_roles}

            # Only add roles that do not already exist
            new_roles = []
            if "adventurer" not in existing_role_names:
                new_roles.append(UserRoleModel(role_name="adventurer"))
            if "avatar" not in existing_role_names:
                new_roles.append(UserRoleModel(role_name="avatar"))
            if "kingdom" not in existing_role_names:
                new_roles.append(UserRoleModel(role_name="kingdom"))
            if "admin" not in existing_role_names:
                new_roles.append(UserRoleModel(role_name="admin"))

            if new_roles:
                session.add_all(new_roles)

        # Commit the new roles to the database
        await session.commit()

        # Optionally retrieve the roles to confirm they were added
        all_roles = await session.execute(select(UserRoleModel))
        all_roles = all_roles.scalars().all()
        print(f"Seeded roles: {[role.role_name for role in all_roles]}")


async def seed_quests():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            quests = [
                Quest(
                    id=uuid.uuid4(),
                    type="Базовий квест",
                    name="Візит до академії",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/basic.png",
                    description="Візит до Академії для отримання першого рівня та вибору базового класу",
                    long_description="Цей квест є першим кроком у вашій пригоді. Відвідайте Академію, щоб розпочати свій шлях та вибрати клас, який буде визначати вашу подальшу кар'єру. Цей вибір матиме вплив на ваші майбутні здібності та можливості.",
                    requirements="Зареєструватися в системі та мати базові навички орієнтації у грі.",
                    award="очки досвіду, підвищення класу",
                    goal="Візит до Академії для отримання першого рівня та вибору базового класу",
                    required_level=0,
                ),
                Quest(
                    id=uuid.uuid4(),
                    type="Рутинний квест",
                    name="Завдання на майстерність",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/routine.png",
                    description="Виконання тестового завдання для отримання артефакту та Мідних Монет",
                    long_description="Цей квест дасть вам можливість отримати базові ресурси та покращити свої навички. Завдання включає проходження тесту, який допоможе вам здобути артефакт та мідні монети для подальших пригод.",
                    requirements="Необхідно мати базовий рівень та пройти початковий квест.",
                    award="очки досвіду, мідні монети, артефакти",
                    goal="Виконання тестового завдання для отримання артефакту та Мідних Монет",
                    required_level=1,
                ),
                Quest(
                    id=uuid.uuid4(),
                    type="Пригодницький квест",
                    name="Підйом на вершину",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/adventure.png",
                    description="Проходження кар’єрного коучинга, навчальних курсів та подібних завдань",
                    long_description="Цей квест відкриває перед вами можливості для професійного зростання та розвитку. Ви пройдете коучинг-сесії та навчальні курси, які допоможуть вам підвищити свої навички та отримати нові можливості.",
                    requirements="Необхідно пройти попередні рівні квестів і мати достатньо очок досвіду.",
                    award="підвищення класу, рівня, артефакти, мідні монети",
                    goal="Проходження кар’єрного коучинга, навчальних курсів та подібних завдань",
                    required_level=2,
                ),
                Quest(
                    id=uuid.uuid4(),
                    type="Багаторазовий квест",
                    name="Майстер вербування",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/reusable.png",
                    description="Залучайте нових учасників за партнерським посиланням",
                    long_description="Цей квест дозволяє вам постійно отримувати нагороди за залучення нових учасників. Діліться своїм партнерським посиланням з друзями і отримуйте очки досвіду кожного разу, коли новий учасник приєднується до гри.",
                    requirements="Мати активний акаунт і доступ до партнерської програми.",
                    award="очки досвіду",
                    goal="Залучайте нових учасників за партнерським посиланням",
                    required_level=3,
                ),
                Quest(
                    id=uuid.uuid4(),
                    type="Командний квест",
                    name="Сила команди",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/team.png",
                    description="Участь у командному проекті для отримання досвіду та Золотих Монет",
                    long_description="Цей квест дозволяє вам працювати в команді для досягнення спільної мети. Завдяки командній роботі ви отримаєте більше досвіду та цінні нагороди, включаючи золоті монети та артефакти.",
                    requirements="Необхідно бути частиною команди та мати базові навички роботи в групі.",
                    award="очки досвіду, золоті та мідні монети, артефакти",
                    goal="Участь у командному проекті для отримання досвіду та Золотих Монет",
                    required_level=4,
                ),
                Quest(
                    id=uuid.uuid4(),
                    type="Битва з міні-босом",
                    name="Виклик міні-босу",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/mini_boss.png",
                    description="Складання онлайн-іспиту для отримання артефакту",
                    long_description="Цей квест є важливою віхою у вашій пригоді. Змагайтеся з міні-босом, щоб скласти іспит і отримати цінний артефакт, який допоможе вам у подальшій подорожі.",
                    requirements="Необхідно мати середній рівень та попередньо отримати базові артефакти.",
                    award="артефакти",
                    goal="Складання онлайн-іспиту для отримання артефакту",
                    required_level=5,
                ),
            ]
            session.add_all(quests)
        await session.commit()


async def seed_achievements():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            achievements = [
                Achievement(
                    id=uuid.uuid4(),
                    name="Початківець",
                    description="Отримати перший рівень",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_1.png",
                ),
                Achievement(
                    id=uuid.uuid4(),
                    name="Новачок",
                    description="Завершити базове навчання",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_2.png",
                ),
                Achievement(
                    id=uuid.uuid4(),
                    name="Дослідник",
                    description="Виконати 3 різні квести",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_3.png",
                ),
                Achievement(
                    id=uuid.uuid4(),
                    name="Воїн",
                    description="Здобути 5 артефактів",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_4.png",
                ),
                Achievement(
                    id=uuid.uuid4(),
                    name="Командир",
                    description="Завершити командний квест",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_5.png",
                ),
                Achievement(
                    id=uuid.uuid4(),
                    name="Маг",
                    description="Досягнути 10-го рівня",
                    image_url="https://quests-app-bucket.s3.eu-north-1.amazonaws.com/images/achievement_6.png",
                ),
            ]
            session.add_all(achievements)
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
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт першого рівня",
                    quest_id=quests[0].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт другого рівня",
                    quest_id=quests[1].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт третого рівня",
                    quest_id=quests[2].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт четвертого рівня",
                    quest_id=quests[3].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт п'ятого рівня",
                    quest_id=quests[4].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                Reward(
                    id=uuid.uuid4(),
                    description="Артефакт шостого рівня",
                    quest_id=quests[5].id,
                    coins=200,
                    points=100,
                    level_increase=1,
                ),
                # Add more rewards as needed
            ]
            session.add_all(rewards)
        await session.commit()


# Seeding logic
async def main():
    # Create tables first
    await create_tables()

    # Check if the database is empty
    if await is_database_empty():
        print("Database is empty, performing seeding...")
        await seed_roles()
        await seed_quests()
        await seed_achievements()
        await seed_rewards()
    else:
        print("Database is not empty, skipping seeding.")


if __name__ == "__main__":
    asyncio.run(main())
