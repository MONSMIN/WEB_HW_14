from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks
from starlette.responses import RedirectResponse
from src.services.email import send_email

from src.database.db import get_db
from src.schemas import UserSchema, UserResponseSchema, TokenModel
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, background_tasks: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)):
    """
        Register a new user.

        Parameters:
        - body (UserSchema): The user data to be registered.
        - background_tasks (BackgroundTasks): Background tasks for sending email.
        - request (Request): The incoming HTTP request.
        - db (AsyncSession): The asynchronous database session.

        Returns:
        - dict: A dictionary containing the user details and a success message.
        """

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
       Log in a user and generate access and refresh tokens.

       Parameters:
       - body (OAuth2PasswordRequestForm): The login credentials.
       - db (AsyncSession): The asynchronous database session.

       Returns:
       - dict: A dictionary containing access and refresh tokens.
       """
    user = await repository_users.get_user_by_email(body.username, db)
    # Only for publicly available services
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    """
        Refresh an access token using a refresh token.

        Parameters:
        - credentials (HTTPAuthorizationCredentials): The refresh token credentials.
        - db (AsyncSession): The asynchronous database session.

        Returns:
        - dict: A dictionary containing new access and refresh tokens.
        """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/{username}')
async def refresh_token(username: str, db: AsyncSession = Depends(get_db)):
    """
        Endpoint for a specific user's action.

        Parameters:
        - username (str): The username of the user.
        - db (AsyncSession): The asynchronous database session.

        Returns:
        - RedirectResponse: A response redirecting to a URL.
        """
    print("------------------------")
    print(f"{username} відкрив наш email")
    print("------------------------")
    return RedirectResponse("http://localhost:8000/static/check.png")


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
        Confirm a user's email using a verification token.

        Parameters:
        - token (str): The verification token.
        - db (AsyncSession): The asynchronous database session.

        Returns:
        - dict: A dictionary containing a success message.
        """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}
