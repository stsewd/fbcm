# Football Championship Manager

## Description

A football championship manager using flask and ponyORM on the
server side; and bootstrap and pjax on the client side.

## Requeriments

- A mysql DBMS
- Python3
- A unix like OS (optional)

## Installation

It's recommended to use a [virtualenv](https://virtualenv.pypa.io/).

- Make a database named `fbcm` or with any other name, but you must changed on the `config.py` file too.
- Install the dependecies with `pip install -r requeriments.txt`.
- Run the command `python manage.py server` or `make run`.
- Run the tests with `make test`
- Populate the database with sample data using `make populate`.

## DOCS

- [ER Diagram](https://editor.ponyorm.com/user/stsewd/football_championship)
