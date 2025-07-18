import asyncio
import json
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import patch
from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "test user",
    "email": "test1@mail.com",
    "avatar": "",
    "password": "123",
    "role": "user",
}

redis_test_user = {
    "id": "1",
    "username": "test user",
    "email": "test1@mail.com",
    "avatar": "",
    "password": "123",
    "role": "admin",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="<https://twitter.com/gravatar>",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token


# @pytest.fixture(scope="module", autouse=True)
# def mock_redis():
#     with patch("src.database.redis.redis_cache") as mocked_redis:
#         mocked_redis.get.return_value = json.dumps(redis_test_user).encode("utf-8")
#         yield mocked_redis


@pytest.fixture(scope="module")
def mock_redis():
    user = User(
        id=1,
        username=redis_test_user["username"],
        email=redis_test_user["email"],
        hashed_password=Hash().get_password_hash(redis_test_user["password"]),
        confirmed=True,
        avatar=redis_test_user["avatar"],
        role="admin",
    )
    with patch("src.services.auth.redis_cache") as mocked_redis:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "role": user.role,
        }
        mocked_redis.get.return_value = json.dumps(user_dict).encode("utf-8")
        mocked_redis.set.return_value = True
        mocked_redis.expire.return_value = True
        yield mocked_redis
