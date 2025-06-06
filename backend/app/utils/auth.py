from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    id: int
    username: str
    role: str

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        username: str = payload.get("username")
        role: str = payload.get("role")
        if user_id is None or username is None or role is None:
            raise credentials_exception
        user = User(id=user_id, username=username, role=role)
        return user
    except JWTError:
        raise credentials_exception

def require_roles(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
