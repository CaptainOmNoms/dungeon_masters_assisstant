from apistar import Include, Route, Command, interfaces
# from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
from apistar.backends import sqlalchemy_backend
from apistar.backends.sqlalchemy_backend import Session
import typing
from monster_tracker import models
from monster_tracker.schema import Hero, Monster, MonsterRepr, HeroRepr
from monster_tracker.utils import get_input
from monster_tracker.test_component import test_routes


def welcome(name=None):
    if name is None:
        return {'message': 'Welcome to API Star!'}
    return {'message': 'Welcome to API Star, %s!' % name}


def create_hero(session: Session, current_app: interfaces.App, hero: Hero = None):
    """
    Creates a Hero - a PC or NPC
    """
    if hero:
        h = models.Hero(**hero)
    elif not isinstance(current_app, App):
        def cond(name):
            (lambda x: x > 0, '{} must be above 0'.format(name))
        name = get_input('Name')
        health = get_input('Max Health', out_type=int, conditions=cond('Health'))
        ac = get_input('AC', out_type=int, conditions=cond('AC'))
        ib = get_input('Initiative Bonus', out_type=int, conditions=cond('Initiative Bonus'))
        speed = get_input('Speed', out_type=int, conditions=cond('Speed'))
        h = models.Hero(name=name, max_health=health, armor_class=ac, initiative_bonus=ib, speed=speed)
    else:
        raise ValueError('Missing value for hero in WSGI App')
    session.add(h)
    session.flush()
    return {'id': h.id, 'name': h.name}


def all_heroes(session: Session, app: interfaces.App) -> typing.List[Hero]:
    """
    A list of all Heroes
    """
    queryset = session.query(models.Hero).all()
    if isinstance(app, App):
        return [Hero(record) for record in queryset]
    return [HeroRepr(record) for record in queryset]


hero_routes = [
    Route('/', 'POST', create_hero),
    Route('/', 'GET', all_heroes)
]

hero_commands = [
    Command('create_hero', create_hero),
    Command('list_heroes', all_heroes)
]


def create_monster(session: Session, monster: Monster):
    """
    Create a new monster
    """
    monster = models.Monster(**monster)
    session.add(monster)
    session.flush()
    return {'id': monster.id, 'name': monster.name}


def all_monsters(session: Session, app: interfaces.App) -> typing.List[Monster]:
    """
    A list of all Monsters
    """
    queryset = session.query(models.Monster).all()
    if isinstance(app, App):
        return [Monster(record) for record in queryset]
    return [MonsterRepr(record) for record in queryset]


monster_routes = [
    Route('/', 'POST', create_monster),
    Route('/', 'GET', all_monsters)
]

monster_commands = [
    Command('create_monster', create_monster),
    Command('all_monsters', all_monsters)
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
        'METADATA': models.Base.metadata
    }
}

commands = hero_commands + monster_commands

app = App(
    routes=routes + test_routes,
    components=sqlalchemy_backend.components,
    settings=settings,
    commands=commands + sqlalchemy_backend.commands
)


if __name__ == '__main__':
    app.main()
