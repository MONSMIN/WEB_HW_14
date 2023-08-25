import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.db import Base


class Contact(Base):
    """
       The Contact class represents a contact in the database.

       Attributes:
       - id (int): The unique identifier of the contact.
       - first_name (str): The first name of the contact.
       - last_name (str): The last name of the contact.
       - email (str): The email address of the contact (unique).
       - phone_number (str): The phone number of the contact.
       - birthday (datetime): The birthday of the contact.
       - created_date (datetime): The date when the contact was created.
       - update_date (datetime): The date when the contact was last updated.
       - user_id (int): The ID of the user associated with the contact.
       - user (User): The associated User object.
       """

    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String)
    birthday = Column(DateTime)
    created_date = Column(DateTime, default=date.today, nullable=True)
    update_date: Mapped[date] = Column(DateTime, default=date.today, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship('User', backref="contacts")


class User(Base):
    """
       The User class represents a user in the database.

       Attributes:
       - id (int): The unique identifier of the user.
       - username (str): The username of the user.
       - email (str): The email address of the user (unique).
       - password (str): The password of the user.
       - created_at (datetime): The date when the user was created.
       - updated_at (datetime): The date when the user was last updated.
       - avatar (str): The path to the user's avatar.
       - refresh_token (str): The refresh token associated with the user.
       - confirmed (bool): Indicates if the user's account is confirmed.
       """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
