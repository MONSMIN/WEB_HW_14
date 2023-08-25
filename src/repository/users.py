import logging

from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserSchema


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
        Retrieve a user by their email address.

        Parameters:
        - email (str): The email address of the user to retrieve.
        - db (AsyncSession): The asynchronous database session.

        Returns:
        - User | None: The retrieved User object or None if not found.
        """
    sq = select(User).filter_by(email=email)
    result = await db.execute(sq)
    user = result.scalar_one_or_none()
    logging.info(user)
    return user


async def create_user(body: UserSchema, db: AsyncSession) -> User:
    """
    The create_user function creates a new user in the database.

        :param body: UserSchema: Validate the request body and convert it to a user object
        :param db: AsyncSession: Pass the database session to the function
        :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        logging.error(e)
    new_user = User(**body.model_dump(), avatar=avatar)  # User(username=username, email=email, password=password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

        :param user: User: Identify the user that is being updated
        :param token: str | None: Update the user's refresh token
        :param db: AsyncSession: Pass the database session to the function

        return: None, updates the user's refresh token in the database

    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.

    :param email: str: Identify the user
    :param db: AsyncSession: Pass the database session to the function

    return: None ,updates the user's confirmed status to true

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Get the user from the database
    :param url: str: Specify the type of data that is expected to be passed in
    :param db: AsyncSession: Pass the database session into the function

    return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
