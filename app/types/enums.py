from enum import Enum

class UserType(Enum):
    """Enum for user types."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    """Enum for user types."""
    CLIENT = "client"
    """Enum for user types."""
    

class AuthType(Enum):
    """Enum for OAuth flow"""
    OAUTH = "oauth"
    OIDC = "oidc"
    SSO = "sso"
    
