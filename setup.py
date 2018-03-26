from setuptools import setup, find_packages

setup(
    name='monster_tracker',
    version='0.1dev',
    packages=find_packages(),
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='An Encounter runner for Dungeons and Dragons 5e',
    install_requires=[
        'cmd2>=0.8.0,<1.0.0', 'sqlalchemy>=1.2.4,<2.0.0', 'marshmallow_sqlalchemy>=0.13,<1.0.0', 'more-itertools',
        'tabulate', 'pyyaml', 'python-cli-ui', 'apistar'
    ]
)
