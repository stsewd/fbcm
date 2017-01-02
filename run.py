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


if __name__ == "__main__":
    cli()
