import click


@click.group()
def cli():
    pass


@cli.command()
def server():
    from fbcm import app
    app.run(debug=True)


@cli.command()
def initdb():
    from fbcm import db
    from fbcm import models
    db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    cli()
