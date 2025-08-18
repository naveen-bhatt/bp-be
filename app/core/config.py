"""Application configuration using Pydantic settings."""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: Optional[str] = Field(default="BP Backend", description="Application name")
    environment: Optional[str] = Field(default="dev", alias="ENV", description="Environment (dev/prod)")
    debug: Optional[bool] = Field(default=False, description="Debug mode")
    
    # Security
    secret_key: Optional[str] = Field(default=None, description="Secret key for JWT signing")
    jwt_algorithm: Optional[str] = Field(default="HS256", description="JWT algorithm")
    access_token_ttl_minutes: Optional[int] = Field(default=30, description="Access token TTL in minutes")
    refresh_token_ttl_days: Optional[int] = Field(default=7, description="Refresh token TTL in days")
    
    # Database
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # CORS
    cors_origins: Optional[str] = Field(
        default="http://localhost:3000",
        description="Comma-separated CORS origins"
    )
    
    # Frontend
    frontend_url: Optional[str] = Field(
        default="http://localhost:3000",
        description="Frontend application URL for OAuth redirects"
    )
    
    # OAuth Providers
    google_client_id: Optional[str] = Field(default=None, description="Google OAuth client ID")
    google_client_secret: Optional[str] = Field(default=None, description="Google OAuth client secret")
    github_client_id: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    github_client_secret: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    apple_team_id: Optional[str] = Field(default=None, description="Apple team ID")
    apple_key_id: Optional[str] = Field(default=None, description="Apple key ID")
    apple_private_key_path: Optional[str] = Field(default=None, description="Apple private key file path")
    
    # Payment Providers
    stripe_secret_key: Optional[str] = Field(default=None, description="Stripe secret key")
    stripe_webhook_secret: Optional[str] = Field(default=None, description="Stripe webhook secret")
    razorpay_key_id: Optional[str] = Field(default=None, description="Razorpay key ID")
    razorpay_key_secret: Optional[str] = Field(default=None, description="Razorpay key secret")
    
    # Admin User (for seeding)
    admin_email: Optional[str] = Field(default="admin@example.com", description="Admin user email")
    admin_password: Optional[str] = Field(default="admin123", description="Admin user password")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        # Always include the main domains
        default_origins = [
            "http://localhost:3000",
            "https://bluepansy.in", 
            "https://beta.bluepansy.in", 
            "https://qa.bluepansy.in", 
            "https://dev.bluepansy.in"
        ]
        
        # If custom CORS origins are provided and not empty, use them
        if self.cors_origins and self.cors_origins.strip():
            custom_origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
            if custom_origins:
                logger.info(f"Using custom CORS origins: {custom_origins}")
                return custom_origins
        
        # Return default origins
        logger.info(f"Using default CORS origins: {default_origins}")
        return default_origins
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate and normalize environment value."""
        v = v.lower().strip()
        # Map common environment names to our standard values
        env_mapping = {
            "dev": "dev",
            "development": "dev",
            "local": "dev",
            "prod": "prod",
            "production": "prod",
            "staging": "prod"
        }
        
        if v in env_mapping:
            return env_mapping[v]
        
        raise ValueError(f"Environment must be one of: {list(env_mapping.keys())}")
    
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "prod"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment in ["dev", "local", "qa", "beta"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()

# Debug logging for CORS configuration
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS origins from env: '{settings.cors_origins}'")
logger.info(f"CORS origins type: {type(settings.cors_origins)}")
logger.info(f"CORS origins is None: {settings.cors_origins is None}")
logger.info(f"CORS origins is empty string: {settings.cors_origins == ''}")
logger.info(f"CORS origins list: {settings.cors_origins_list}")
logger.info(f"Environment: {settings.environment}")