import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import User, Contact
from src.schemas import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="test user",
        email="test@mail.com",
        avatar="",
        hashed_password="123",
        role="user",
    )


@pytest.fixture
def fake_contact(user):
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@mail.com",
        phone="+380503355444",
        birthday="2000-01-01",
        note="note",
        user=user,
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, fake_contact):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_contact]
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.get_contacts(skip=0, limit=10, user=user)
    assert len(result) == 1
    assert result[0].first_name == "John"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user, fake_contact):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.get_contact_by_id(1, user)
    assert result == fake_contact
    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):

    body = ContactModel(
        first_name="Piter",
        last_name="Folk",
        email="piter@gmail.com",
        phone="+380667474555",
        birthday="2000-01-01",
        note="Some text",
    )

    result = await contact_repository.create_contact(body=body, user=user)
    assert isinstance(result, Contact)
    assert result.first_name == "Piter"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user, fake_contact):
    body = ContactModel(
        first_name="Piter",
        last_name="Folk",
        email="piter@gmail.com",
        phone="+380667474555",
        birthday="2000-01-01",
        note="Some text",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.update_contact(contact_id=1, body=body, user=user)
    assert result is not None
    assert result.last_name == "Folk"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, fake_contact):

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.remove_contact(contact_id=1, user=user)
    assert result is not None
    assert result.first_name == "John"
    mock_session.delete.assert_awaited_once_with(fake_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_contacts(contact_repository, mock_session, user, fake_contact):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_contact]
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.search_contacts(
        skip=0,
        limit=10,
        first_name=None,
        last_name=None,
        email="john@mail.com",
        user=user,
    )
    assert len(result) == 1
    assert result is not None
    assert result[0].id == 1
    assert result[0].first_name == "John"


@pytest.mark.asyncio
async def test_get_birthdays(contact_repository, mock_session, user):

    fake_contact_1 = Contact(
        id=1,
        first_name="Contact 1",
        last_name="Contact 1",
        email="contact1@mail.com",
        phone="+380503355441",
        birthday=(datetime.now() + timedelta(days=1)).date(),
        note="note",
        user=user,
    )

    fake_contact_2 = Contact(
        id=2,
        first_name="Contact 2",
        last_name="Contact 2",
        email="contact2@mail.com",
        phone="+380503355442",
        birthday=(datetime.now() + timedelta(days=6)).date(),
        note="note",
        user=user,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_contact_1, fake_contact_2]
    mock_session.execute = AsyncMock(return_value=mock_result)
    result = await contact_repository.get_birthdays(
        skip=0,
        limit=10,
        user=user,
    )
    assert len(result) == 2
    assert result is not None
