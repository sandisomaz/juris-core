import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from src.core.config import settings
from src.core.security import hash_password
from src.storage.models import Base, UserDB, MatterDB, DocumentDB

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an active async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Creates database tables and seeds default user/matter records if not present."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Seed admin user if not exists
        stmt = select(UserDB).where(UserDB.username == "counsel")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            default_user = UserDB(
                id=str(uuid.uuid4()),
                username="counsel",
                email="counsel@juriscore.io",
                hashed_password=hash_password("generate_a_secure_random_key_min_32_chars"),
                full_name="Senior Compliance Counsel",
                role="Senior Compliance Counsel"
            )
            session.add(default_user)

        # Seed initial matter if not exists
        m_stmt = select(MatterDB).where(MatterDB.id == "m-001")
        m_res = await session.execute(m_stmt)
        matter = m_res.scalar_one_or_none()

        if not matter:
            default_matter = MatterDB(
                id="m-001",
                title="ABC Logistics Vendor Onboarding & POPIA Audit",
                client_name="ABC Logistics Ltd",
                jurisdiction="South Africa",
                status="ACTIVE",
                risk_score=62.0
            )
            session.add(default_matter)

        await session.commit()
