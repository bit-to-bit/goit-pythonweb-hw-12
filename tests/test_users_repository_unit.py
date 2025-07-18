import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def fake_user():
    return User(
        id=1,
        username="test user 1",
        email="test1@mail.com",
        avatar="",
        hashed_password="123",
        role="user",
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, fake_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await user_repository.get_user_by_id(1)
    assert result == fake_user
    assert result is not None
    assert result.id == 1
    assert result.username == "test user 1"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, fake_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await user_repository.get_user_by_username("test user 1")
    assert result == fake_user
    assert result is not None
    assert result.id == 1
    assert result.email == "test1@mail.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, fake_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await user_repository.get_user_by_email("test1@mail.com")
    assert result == fake_user
    assert result is not None
    assert result.id == 1
    assert result.email == "test1@mail.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):

    body = UserCreate(
        username="UserCreate", email="user_create@mail.com", password="123"
    )

    result = await user_repository.create_user(body=body)
    assert isinstance(result, User)
    assert result.username == "UserCreate"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, fake_user):

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await user_repository.update_avatar_url(
        email="test1@mail.com", url="https://www.google.com/my_avatar.png"
    )
    assert isinstance(result, User)
    assert result.avatar == "https://www.google.com/my_avatar.png"
    assert result is not None
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_user)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, fake_user):

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    await user_repository.confirmed_email(email="test1@mail.com")
    result = await user_repository.get_user_by_email(email="test1@mail.com")
    assert result.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password(user_repository, mock_session, fake_user):

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await user_repository.update_password(
        email="test1@mail.com", password="555"
    )
    assert isinstance(result, User)
    assert result.hashed_password == "555"
    assert result is not None
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_user)
