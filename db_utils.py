import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from dotenv import load_dotenv
import os
from base import Base

load_dotenv()

# PostgreSQL Async Database URL (replace with your actual database credentials)
db_user = os.getenv('POSTGRES_USER')
db_name = os.getenv('POSTGRES_DB')
db_password = os.getenv('POSTGRES_PASSWORD')
db_port = 5432
db_host = os.getenv('DB_HOST', 'localhost')

DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        """Create all tables defined in the metadata."""
        async with self.engine.begin() as conn:
            # Create all tables defined in the metadata
            await conn.run_sync(Base.metadata.create_all)
        print('created tables')

    async def add_or_save(self, obj):
        """Add an ORM object to the database."""
        async with self.Session() as session:
            async with session.begin():
                session.add(obj)
            await session.commit()

    async def delete(self, obj):
        """Delete an ORM object from the database."""
        async with self.Session() as session:
            async with session.begin():
                await session.delete(obj)
            await session.commit()

    async def fetch_all(self, model, filters=None):
        """Fetch all objects of a specific model with optional filters."""
        async with self.Session() as session:
            # Start building the query
            stmt = select(model)
            
            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    stmt = stmt.filter(getattr(model, column) == value)

            result = await session.execute(stmt)
            return result.scalars().all()  # Return all matching records

    async def fetch_one(self, model, filters=None):
        """Fetch a single object of a specific model with optional filters."""
        async with self.Session() as session:
            # Start building the query
            stmt = select(model)
            
            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    stmt = stmt.filter(getattr(model, column) == value)

            result = await session.execute(stmt)
            return result.scalars().first()  # Return the first matching record, or None

    async def update_one_or_more(self, model, filters, updates):
        """Update one or more objects of the specified model with the given filters and new data."""
        async with self.Session() as session:
            # Start building the query
            stmt = select(model).filter_by(**filters)
            
            result = await session.execute(stmt)
            instances = result.scalars().all()
    
            if instances:
                for instance in instances:
                    for key, value in updates.items():
                        setattr(instance, key, value)
    
                # We don't need to call session.begin() again if we're already within the transaction context.
                # Simply add the instances to the session and commit.
                session.add_all(instances)  # Use add_all to add multiple instances at once
                await session.commit()
    
                return instances  # Return the list of updated instances
            else:
                return []  # Return an empty list if no records were found
    

    async def execute_raw(self, query, params=None):
        """Execute a raw SQL query if needed (fallback option)."""
        async with self.Session() as session:
            async with session.begin():
                result = await session.execute(text(query), params)
            return result

# Create the database manager instance
db_manager = DatabaseManager(database_url=DATABASE_URL)
