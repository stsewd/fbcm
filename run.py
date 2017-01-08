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
    populate_persons()
    populate_teams()


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
                    lastname=fake.last_name()
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


if __name__ == "__main__":
    cli()
