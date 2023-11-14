from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime
from aiogram.types import User as AiogramUser
from sqlalchemy import func


DATABASE_URL = "postgresql+asyncpg://mot:123@localhost/database"

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    @classmethod
    async def create_table(cls, engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def add_user(cls, session, aiogram_user: AiogramUser):
        # Проверка наличия пользователя в базе данных
        async with session.begin() as txn:
            existing_user = await cls.user_exists(session, aiogram_user.id)
            if existing_user is None:
                # Создание записи в базе данных
                new_user = cls(
                    user_id=aiogram_user.id,
                    username=aiogram_user.username,
                    first_name=aiogram_user.first_name,
                    last_name=aiogram_user.last_name
                )
                # Добавление нового пользователя и коммит изменений
                session.add(new_user)
                await txn.commit()

                print(
                    f"Добавлен пользователь: {aiogram_user.id}, {aiogram_user.username}, {aiogram_user.first_name}, {aiogram_user.last_name}")
                return True
            else:
                existing_user.timestamp = datetime.utcnow()
                await txn.commit()

                print(f"Обновлена дата для пользователя с ID {aiogram_user.id}")
                return False

    @classmethod
    async def user_exists(cls, session, user_id):
        query = await session.execute(select(cls).where(cls.user_id == user_id))
        existing_user = query.scalar()
        return existing_user

    @classmethod
    async def count_users(cls, session):
        query = await session.execute(select(func.count()).select_from(cls))
        count = query.scalar()
        return count

    @classmethod
    async def get_user_date(cls, session, user_id):
        existing_user = await cls.user_exists(session, user_id)
        if existing_user:
            return existing_user.timestamp
        else:
            print(f"Пользователь с ID {user_id} не найден в базе данных.")
            return None


def create_engine_and_session():
    engine = create_async_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async_session = Session()
    return engine, async_session
