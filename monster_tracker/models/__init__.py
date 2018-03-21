from enum import IntEnum

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()  # pylint: disable=invalid-name

Status = IntEnum('Status', 'DEAD ALIVE UNCONSCIOUS STABLE')  # pylint: disable=invalid-name


def create_session(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


from .characters import Character
from .monster import Monster
from .hero import Hero
from .encounter import Encounter

s = create_session('sqlite:///:memory:')()  # pylint: disable=invalid-name

__all__ = ['Character', 'Monster', 'Hero', 'Encounter', 'create_session', 'Status', 'Base', 's']
