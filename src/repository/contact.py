from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Session
from sqlalchemy import func

from sqlalchemy import select

from src.database.models import Contact, User
from src.schemas import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
        The get_contacts function returns a list of contacts for the user.

        :param limit: int: Limit the number of contacts returned
        :param offset: int: Specify the offset of the query
        :param db: AsyncSession: Pass in the database session
        :param user: User: Get the contacts for a specific user
        :return: A list of contact objects
        :doc-author: Trelent
    """
    sq = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(sq)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
        The get_contact function returns a contact from the database.

        :param contact_id: int: Specify the id of the contact to be retrieved
        :param db: AsyncSession: Pass the database connection to the function
        :param user: User: Get the user from the database
        :return: A contact object
    """
    contact = await db.execute(select(Contact).where(Contact.id == contact_id, user=user))
    return contact.scalars().first()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
        Create a new contact and store it in the database.

        Parameters:
        - body (ContactSchema): The contact data to be created.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The associated User object.

        Returns:
        - contact: The created Contact object.
        """

    contact_data = {
        "first_name": body.first_name,
        "last_name": body.last_name,
        "email": body.email,
        "phone_number": body.phone_number,
        "birthday": body.birthday,
        "created_date": body.created_date
    }

    contact = Contact(**contact_data, user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """
        Update an existing contact in the database.

        Parameters:
        - contact_id (int): The ID of the contact to update.
        - body (ContactUpdateSchema): The updated contact data.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The associated User object.

        Returns:
        - contact: The updated Contact object or None if not found.
        """
    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.update_date = body.update_date
        await db.commit()
        await db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
        Remove a contact from the database.

        Parameters:
        - contact_id (int): The ID of the contact to remove.
        - body (ContactSchema): The contact data.
        - db (AsyncSession): The asynchronous database session.
        - user (User): The associated User object.

        Returns:
        - contact: The removed Contact object or None if not found.
        """

    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(db):
    """
     Retrieve upcoming birthdays within the next 7 days.

     Parameters:
     - db (AsyncSession): The asynchronous database session.

     Returns:
     - List[Contact]: A list of Contact objects representing upcoming birthdays.
     """
    today = datetime.now().date()
    end_date = today + timedelta(days=7)

    contacts = select(Contact).where(Contact.birthday >= today).where(Contact.birthday <= end_date)
    result = await db.execute(contacts)

    upcoming_birthdays = result.scalars().all()
    return upcoming_birthdays
