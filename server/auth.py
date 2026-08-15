from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User


# ======================================================
# JWT CONFIGURATION
# ======================================================

SECRET_KEY = "jobhub-super-secret-key-change-this-later"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


# ======================================================
# SECURITY
# ======================================================

security = HTTPBearer(
    auto_error=False
)


# ======================================================
# DATABASE
# ======================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ======================================================
# CREATE ACCESS TOKEN
# ======================================================

def create_access_token(
    user_id: int,
    email: str,
    role: str
):

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ======================================================
# GET CURRENT USER
# ======================================================

def get_current_user(
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(security),

    db: Session = Depends(get_db)
):

    # --------------------------------------------------
    # Check authorization header
    # --------------------------------------------------

    if credentials is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )


    token = credentials.credentials


    # --------------------------------------------------
    # Decode JWT
    # --------------------------------------------------

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")


        if user_id is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )


        try:

            user_id = int(user_id)

        except (TypeError, ValueError):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )


    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


    # --------------------------------------------------
    # Find user
    # --------------------------------------------------

    user = db.query(User).filter(
        User.id == user_id
    ).first()


    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )


    return user


# ======================================================
# REQUIRE JOB SEEKER
# ======================================================

def require_job_seeker(
    current_user: User = Depends(
        get_current_user
    )
):

    allowed_roles = [
        "job_seeker",
        "jobseeker"
    ]


    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can perform this action"
        )


    return current_user


# ======================================================
# REQUIRE EMPLOYER
# ======================================================

def require_employer(
    current_user: User = Depends(
        get_current_user
    )
):

    if current_user.role != "employer":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can perform this action"
        )


    return current_user