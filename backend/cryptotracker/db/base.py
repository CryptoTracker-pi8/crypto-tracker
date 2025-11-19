"""
Declarative base for all SQLAlchemy models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class that all SQLAlchemy models should extend.
    """

    pass

