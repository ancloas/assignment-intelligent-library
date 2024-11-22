import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from dotenv import load_dotenv
import os
from models import Base, Book, Review

load_dotenv()

# PostgreSQL Async Database URL (replace with your actual database credentials)
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT', 5432)

DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@localhost:{db_port}/{db_name}"

class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            # Create all tables defined in the metadata
            await conn.run_sync(Base.metadata.create_all)

    async def execute(self, query, params=None):
        async with self.Session() as session:
            async with session.begin():
                result = await session.execute(text(query), params)
                return result

    async def fetch_all(self, query, params=None):
        result = await self.execute(query, params)
        return result.fetchall()

    async def fetch_one(self, query, params=None):
        result = await self.execute(query, params)
        return result.fetchone()

    async def add(self, obj):
        async with self.Session() as session:
            async with session.begin():
                session.add(obj)
                await session.commit()

    # async def update(self, obj):
    #     async with self.Session() as session:
    #         async with session.begin():
    #             # Assume obj is already attached to the session
    #             await session.commit()

    # async def delete(self, obj):
    #     async with self.Session() as session:
    #         async with session.begin():
    #             await session.delete(obj)
    #             await session.commit()

# Create the database manager instance
db_manager = DatabaseManager(database_url=DATABASE_URL)
