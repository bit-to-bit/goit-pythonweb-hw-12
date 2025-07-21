from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas import ContactModel
from sqlalchemy.exc import IntegrityError


def _handle_integrity_error(e: IntegrityError):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Помилка цілісності даних:",
    )


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        try:
            return await self.repository.update_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.repository.remove_contact(contact_id, user)

    async def search_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str,
        last_name: str,
        email: str,
        user: User,
    ):
        return await self.repository.search_contacts(
            skip, limit, first_name, last_name, email, user
        )

    async def get_birthdays(self, skip: int, limit: int, user: User):
        return await self.repository.get_birthdays(skip, limit, user)
