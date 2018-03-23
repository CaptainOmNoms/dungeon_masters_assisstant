from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from apistar import Route, Include, http
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.backends import sqlalchemy_backend
from apistar.backends.sqlalchemy_backend import Session
from monster_tracker.models import *


def create_hero(session: Session, request: http.Request):
    hero = Hero(**request.RequestData)
    session.add(hero)
    session.flush()
    return {'id': hero.id, 'name': hero.name}

hero_routes = [Route('/', 'POST', create_hero)]

def create_monster(session: Session, max_health: int, ac: int, initiative_bonus: int, initiative: int, speed: int,
                   current_health: int, temp_health: int):
    monster = Monster(max_health, ac, initiative_bonus, initiative, speed, current_health, temp_health)
    session.add(monster)
    session.flush()
    return {'id': monster.id, 'current_health': monster.current_health}

monster_routes = [Route('/', 'POST', create_monster)]


routes = [
    Include('/heroes', hero_routes),
    Include('/monsters', monster_routes)
]

commands = [
    'create_hero', create_hero,
    'create_monster', create_monster
]

settings = {
    'DATABASE': {
        'URL': 'sqlite://:memory:',
        'METADATA': Base.metadata
    }
}

app = App(
    routes=routes,
    settings=settings,
    commands=sqlalchemy_backend.commands,
    components=sqlalchemy_backend.components
)
