import click
from pony import orm


@click.group()
def cli():
    pass


@cli.command()
def server():
    from fbcm import app
    orm.sql_debug(app.config['DEBUG'])
    app.run(debug=True)


@cli.command()
def clean_database():
    from fbcm.models import db
    db.drop_all_tables(with_all_data=True)


@cli.command()
def populate():
    populate_positions()
    populate_persons(20*11)
    populate_teams(20)
    populate_championships()
    register_players_on_teams()
    register_teams_to_championship()


def populate_persons(n=50):
    from faker import Faker
    from pony.orm import db_session
    from fbcm.models import Player

    fake = Faker()
    with db_session:
        for _ in range(n):
            try:
                Player(
                    id=fake.numerify('#' * 10),
                    name=fake.first_name(),
                    lastname=fake.last_name(),
                )
            except Exception:
                continue


def populate_teams(n=32):
    from faker import Faker
    from pony.orm import db_session
    from fbcm.models import Team

    fake = Faker()
    with db_session:
        for _ in range(n):
            try:
                Team(name=fake.country())
            except Exception:
                continue


def populate_championships():
    from pony.orm import db_session
    from fbcm.models import Championship
    from fbcm.views import add_default_stages

    with db_session:
        c = Championship(
            name="El Campeonato",
            description="""
                Campeonato de fútbol que será jugado en algún momento del 2017.
            """,
            points_winner=2,
            points_draw=1,
            points_loser=0
        )
        add_default_stages(c)


def register_players_on_teams(num_players=11, num_teams=16):
    from pony.orm import db_session
    from fbcm.models import Team, Player, Position
    #  import random

    with db_session:
        teams = Team.select()[:num_teams]

        for page, team in enumerate(teams, 1):
            players = Player.select().page(page, pagesize=num_players)
            for number, player in enumerate(players):
                player.set(
                    number=number,
                    position=Position.select_random(1)[:1][0]
                )
            team.set(
                players=players
            )


def register_teams_to_championship(n=16):
    from pony.orm import db_session
    from fbcm.models import Championship, Team

    team_name = "El Campeonato"
    with db_session:
        championship = Championship.get(name=team_name)
        for team in Team.select()[:n]:
            team.championships.create(
                championship=championship
            )


def populate_positions():
    from pony.orm import db_session
    from fbcm.models import Position

    with db_session:
        for position in (
                'arquero', 'defensa', 'delantero', 'mediocampista'):
            Position(name=position)


if __name__ == "__main__":
    cli()
