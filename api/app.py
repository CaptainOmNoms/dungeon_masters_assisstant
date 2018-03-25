from apistar import Include, Route, Command, http
# from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
from apistar.backends import sqlalchemy_backend
from apistar.backends.sqlalchemy_backend import Session
from monster_tracker.models import *


def welcome(name=None):
    if name is None:
        return {'message': 'Welcome to API Star!'}
    return {'message': 'Welcome to API Star, %s!' % name}


def create_hero(session: Session, request: http.RequestData):
    hero = Hero(**request)
    session.add(hero)
    session.flush()
    return {'id': hero.id, 'name': hero.name}


hero_routes = [Route('/', 'POST', create_hero)]


def create_monster(session: Session, name: str, max_health: int, ac: int, initiative_bonus: int, initiative: int,
                   speed: int, current_health: int, temp_health: int):
    monster = Monster(name=name, max_health=max_health, armor_class=ac, initiative_bonus=initiative_bonus,
                      initiative=initiative, speed=speed, current_health=current_health, temp_health=temp_health)
    session.add(monster)
    session.flush()
    return {'id': monster.id, 'name': monster.name}


def all_monsters(session: Session):
    return list(map(repr, session.query(Monster).all()))


monster_routes = [
    Route('/', 'POST', create_monster),
    Route('/', 'GET', all_monsters)
]


routes = [
    Route('/', 'GET', welcome),
    Include('/docs', docs_urls),
    Include('/static', static_urls),
    Include('/heroes', hero_routes),
    Include('/monsters', monster_routes)
]

settings = {
    'DATABASE': {
        'URL': 'sqlite:///test.db',
        'METADATA': Base.metadata
    }
}

commands = [
    Command('create_monster', create_monster),
    Command('all_monsters', all_monsters)
]

app = App(
    routes=routes,
    components=sqlalchemy_backend.components,
    settings=settings,
    commands=commands + sqlalchemy_backend.commands
)


if __name__ == '__main__':
    app.main()
