from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse
from src.services.contact import ContactService
from src.services.auth import get_current_user
from src.schemas import User

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a paginated list of contacts belonging to the current user.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponse]: A list of contact objects.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    skip: int = 0,
    limit: int = 100,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Search for contacts based on first name, last name, or email.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        first_name (str | None): Filter by first name.
        last_name (str | None): Filter by last name.
        email (str | None): Filter by email.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponse]: A list of matched contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(
        skip, limit, first_name, last_name, email, user
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a single contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The retrieved contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact for the current user.

    Args:
        body (ContactModel): The data of the contact to create.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact by its ID.

    Args:
        body (ContactModel): The new data for the contact.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The deleted contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_birthdays(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts whose birthdays are within the next 7 days.

    Args:
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        db (AsyncSession): The database session dependency.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(skip, limit, user)
    return contacts
