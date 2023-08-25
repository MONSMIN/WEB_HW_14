from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactSchema, ContactUpdateSchema
from src.repository import contact as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a list of contacts.

        Parameters:
        - skip (int): The number of contacts to skip.
        - limit (int): The maximum number of contacts to retrieve.
        - db (Session): The database session.
        - current_user (User): The authenticated User object.

        Returns:
        - List[ContactResponse]: A list of ContactResponse objects representing contacts.
        """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_all(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db),
                  user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a paginated list of contacts.

        Parameters:
        - limit (int): The maximum number of contacts to retrieve.
        - offset (int): The offset for pagination.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The authenticated User object.

        Returns:
        - List[ContactResponse]: A list of ContactResponse objects representing contacts.
        """
    contacts = await repository_contacts.get_contacts(db)
    return contacts[offset:][:limit]


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a specific contact by its ID.

        Parameters:
        - contact_id (int): The ID of the contact to retrieve.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The authenticated User object.

        Returns:
        - ContactResponse: The ContactResponse object representing the contact.
        """
    contact = await repository_contacts.get_contact(contact_id, db, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.post("/", response_model=ContactResponse, description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Create a new contact.

        Parameters:
        - body (ContactSchema): The contact data to be created.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The authenticated User object.

        Returns:
        - ContactResponse: The ContactResponse object representing the created contact.
        """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Update the contact by its ID.

        Parameters:
        - body (ContactUpdateSchema): The updated contact data.
        - contact_id (int): The ID of the contact to update.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The authenticated User object.

        Returns:
        - ContactResponse: The ContactResponse object representing the updated contact.
        """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Delete the contact by its ID.

        Parameters:
        - contact_id (int): The ID of the contact to delete.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The authenticated User object.

        Returns:
        - ContactResponse: The ContactResponse object representing the deleted contact.
        """
    contact = await repository_contacts.remove_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.get("/upcoming-birthdays/", response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    """
        Retrieve the list of contacts with upcoming birthdays.

        Parameters:
        - db (Session): The database session.

        Returns:
        - List[ContactResponse]: A list of ContactResponse objects representing contacts with upcoming birthdays.
        """
    return await repository_contacts.get_upcoming_birthdays(db)
