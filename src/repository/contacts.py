from typing import List
from datetime import date, timedelta
from sqlalchemy import select, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactRepository:
    """
    Repository for performing CRUD operations and queries on contacts.

    Attributes:
        db (AsyncSession): Asynchronous SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve a paginated list of contacts belonging to a user.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            user (User): The owner of the contacts.

        Returns:
            List[Contact]: A list of user contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID for a specific user.

        Args:
            contact_id (int): The contact's ID.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for a specific user.

        Args:
            body (ContactModel): The contact data.
            user (User): The owner of the contact.

        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update an existing contact by ID.

        Args:
            contact_id (int): The contact's ID.
            body (ContactModel): The updated contact data.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.birthday = body.birthday
            contact.email = body.email
            contact.phone = body.phone
            contact.note = body.note
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by ID.

        Args:
            contact_id (int): The contact's ID.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The deleted contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str,
        last_name: str,
        email: str,
        user: User,
    ) -> List[Contact]:
        """
        Search contacts by first name, last name, or email.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            first_name (str): The first name to search for (can be None).
            last_name (str): The last name to search for (can be None).
            email (str): The email to search for (can be None).
            user (User): The owner of the contacts.

        Returns:
            List[Contact]: A list of matched contacts.
        """
        stmt = (
            select(Contact)
            .filter(
                or_(Contact.first_name == first_name, first_name is None),
                or_(Contact.last_name == last_name, last_name is None),
                or_(Contact.email == email, email is None),
            )
            .filter_by(user=user)
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_birthdays(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve contacts with birthdays in the next 7 days.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            user (User): The owner of the contacts.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        date_beg = date.today()
        date_end = date_beg + timedelta(days=7)
        month_day_beg = date_beg.month * 100 + date_beg.day
        month_day_end = date_end.month * 100 + date_end.day
        stmt = (
            select(Contact)
            .filter(
                extract("month", Contact.birthday) * 100
                + extract("day", Contact.birthday)
                >= month_day_beg,
                extract("month", Contact.birthday) * 100
                + extract("day", Contact.birthday)
                <= month_day_end,
            )
            .filter_by(user=user)
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
