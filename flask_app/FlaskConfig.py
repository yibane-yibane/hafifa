import os

#fgds
class FlaskConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI",
                                        "postgresql://postgres:test123@localhost:5432/postgres")
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
