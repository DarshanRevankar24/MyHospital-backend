"""Reset the darshan user password directly via SQLAlchemy."""

import asyncio
import os
import sys

sys.path.insert(0, "/app/src")
os.environ.setdefault("SECRET_KEY", "placeholder")

from crudauth import get_password_hash
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

NEW_PASSWORD = "MyHospital@123"
USERNAME = "darshan"

DB_URL = (
    f"postgresql+asyncpg://"
    f"{os.environ.get('POSTGRES_USER', 'postgres')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
    f"{os.environ.get('POSTGRES_SERVER', 'postgres')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}/"
    f"{os.environ.get('POSTGRES_DB', 'postgres')}"
)


async def reset_password():
    engine = create_async_engine(DB_URL, echo=False)
    hashed = get_password_hash(NEW_PASSWORD)
    print(f"New hash: {hashed}")
    async with AsyncSession(engine) as session:
        await session.execute(
            text("UPDATE public.user SET hashed_password = :h WHERE username = :u"),
            {"h": hashed, "u": USERNAME},
        )
        await session.commit()
    result = await engine.connect()
    async with result as conn:
        row = await conn.execute(
            text("SELECT username, hashed_password FROM public.user WHERE username = :u"),
            {"u": USERNAME},
        )
        r = row.fetchone()
        print(f"DB row: username={r[0]}, hash_prefix={r[1][:20]}")
    await engine.dispose()
    print("Done — password reset to:", NEW_PASSWORD)


asyncio.run(reset_password())
