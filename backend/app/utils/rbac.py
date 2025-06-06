from fastapi import Depends, HTTPException, status
from typing import List
from app.utils.auth import get_current_user

def rbac_required(allowed_roles: List[str]):
    def decorator(current_user = Depends(get_current_user)):
        if current_user.role.lower() not in [role.lower() for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return decorator
