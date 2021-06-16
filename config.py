class Config:
    """Set Flask configuration from .env file."""

    # Database
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:test123@localhost:5432/postgres"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
