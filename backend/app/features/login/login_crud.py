from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import verify_password
from app.features.users.users_crud import get_user_by_email
from app.features.users.users_models import User


async def authenticate(
    *, session: AsyncSession, email: str, password: str
) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
