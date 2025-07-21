from pathlib import Path
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
    Form,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from src.schemas import UserCreate, Token, User, RequestEmail, RequestPassword
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email, send_reset_password_email
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(
    directory=Path(__file__).parent.parent / "services/templates"
)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user and send a confirmation email.

    Args:
        user_data (UserCreate): The registration data for the new user.
        background_tasks (BackgroundTasks): Background task handler.
        request (Request): The current HTTP request.
        db (Session): Database session dependency.

    Returns:
        User: The newly created user object.

    Raises:
        HTTPException: If the email or username already exists.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data with username and password.
        db (Session): Database session dependency.

    Returns:
        Token: Access token for authenticated user.

    Raises:
        HTTPException: If credentials are invalid or email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm user's email address using the verification token.

    Args:
        token (str): Email verification token.
        db (Session): Database session dependency.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If verification fails or email is already confirmed.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ваша електронна пошта вже підтверджена",
        )
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request an email confirmation link to be resent.

    Args:
        body (RequestEmail): Email data of the user.
        background_tasks (BackgroundTasks): Background task handler.
        request (Request): The current HTTP request.
        db (Session): Database session dependency.

    Returns:
        dict: Status message indicating next steps.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/reset_password_email_form", response_class=HTMLResponse)
async def request_reset_password_email(request: Request):
    """
    Serve HTML form to request a password reset email.

    Args:
        request (Request): The current HTTP request.

    Returns:
        HTMLResponse: The rendered password reset form template.
    """
    return templates.TemplateResponse(
        "password_reset_set_email.html", {"request": request}
    )


@router.post("/reset_password_email_form")
async def read_reset_password_email(
    background_tasks: BackgroundTasks,
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Process password reset email request and send reset instructions.

    Args:
        background_tasks (BackgroundTasks): Background task handler.
        request (Request): The current HTTP request.
        email (str): Email address provided in the form.
        db (Session): Database session dependency.

    Returns:
        dict: Status message about reset email dispatch.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        return {"message": "Кориcтувача з такою електронною поштою не існує"}
    background_tasks.add_task(
        send_reset_password_email, user.email, user.username, request.base_url
    )
    return {
        "message": "Перевірте свою електронну пошту для підтвердження скидання пароля"
    }


@router.get("/reset_password/{token}", response_class=HTMLResponse)
async def request_new_password(
    token: str, request: Request, db: Session = Depends(get_db)
):
    """
    Serve HTML form to input a new password using the provided reset token.

    Args:
        token (str): Password reset token.
        request (Request): The current HTTP request.
        db (Session): Database session dependency.

    Returns:
        HTMLResponse: The rendered form for entering a new password.

    Raises:
        HTTPException: If user verification fails.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User verification error"
        )
    return templates.TemplateResponse(
        "password_reset.html", {"request": request, "token": token}
    )


@router.post("/reset_password/{token}")
async def update_password(
    token: str, password: str = Form(...), db: Session = Depends(get_db)
):
    """
    Update user's password using the password reset token.

    Args:
        token (str): Password reset token.
        password (str): The new password.
        db (Session): Database session dependency.

    Returns:
        dict: Confirmation message after password update.

    Raises:
        HTTPException: If user verification fails.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User verification error"
        )
    hashed_password = Hash().get_password_hash(password)
    user_service = UserService(db)
    user = await user_service.update_password(user.email, hashed_password)
    return {"message": f"Пароль для користувача {user.username} змінено"}
