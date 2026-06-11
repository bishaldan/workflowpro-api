from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.enums import OrganizationRole
from app.models.organization import OrganizationMember
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc

    user = db.scalar(select(User).where(User.id == int(subject)))
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_org_member(
    organization_id: int, user: User, db: Session
) -> OrganizationMember:
    membership = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user.id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    return membership


def require_org_writer(
    organization_id: int,
    user: User,
    db: Session,
) -> OrganizationMember:
    membership = require_org_member(organization_id, user, db)
    if membership.role not in {
        OrganizationRole.owner,
        OrganizationRole.admin,
        OrganizationRole.member,
    }:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Write access denied")
    return membership


def require_org_admin(
    organization_id: int,
    user: User,
    db: Session,
) -> OrganizationMember:
    membership = require_org_member(organization_id, user, db)
    if membership.role not in {
        OrganizationRole.owner,
        OrganizationRole.admin,
    }:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access denied")
    return membership


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()
