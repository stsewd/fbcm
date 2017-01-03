import random

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


def get_rand_id():
    return "".join(
        str(random.randint(0, 9))
        for _ in range(10)
    )


@cli.command()
def populate_persons():
    from faker import Faker
    from pony.orm import db_session
    from fbcm.models import Player

    n = 50
    fake = Faker()
    with db_session:
        for i in range(n):
            Player(
                id=get_rand_id(),
                name=fake.first_name(),
                lastname=fake.last_name()
            )


if __name__ == "__main__":
    cli()
