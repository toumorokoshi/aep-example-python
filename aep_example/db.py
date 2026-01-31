from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, ForeignKey

DATABASE_URL = "sqlite+aiosqlite:///./library.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

class DBShelf(Base):
    __tablename__ = "shelves"
    name = Column(String, primary_key=True, index=True) # Resource name is PK
    theme = Column(String)

class DBBook(Base):
    __tablename__ = "books"
    name = Column(String, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    shelf_name = Column(String, ForeignKey("shelves.name"))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
