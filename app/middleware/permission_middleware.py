from app.middleware.auth_middleware import verify_user
from app.types.enums import UserType
from fastapi import Depends, HTTPException, status

RESOURCE_PERMISSIONS = {
    UserType.SUPER_ADMIN: {"view_app"},    
    UserType.ADMIN: {"view_app"},
    UserType.CLIENT: {"create_app", "update_app", "view_app"},
    UserType.USER: {"view_profile"}
}

def has_permission(resourcce: str):
    def check_permission(session = Depends(verify_user)):
        if session.get('user') and session.get('user').user_type:
            if resourcce not in RESOURCE_PERMISSIONS.get(session.get('user').user_type, set()):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You do not have permission for this resource: {resourcce}")
            
        
    return check_permission

