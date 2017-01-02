import click


@click.group()
def cli():
    pass


@cli.command()
def server():
    from fbcm import app
    app.run(debug=True)


if __name__ == "__main__":
    cli()
