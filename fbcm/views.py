from pony.orm import db_session
from flask import (
    abort,
    jsonify,
    redirect,
    render_template,
    url_for
)

from . import app
from .models import FbcmError, Player, Team, Championship
from .forms import PlayerForm, TeamForm, ChampionshipForm


def get_first_error(form):
    if form.errors:
        return list(form.errors.values())[0][0]
    else:
        return ""


@app.route('/')
def index():
    return redirect(url_for('players'))


@app.route('/players/', defaults={'id': None})
@app.route('/players/<id>')
def players(id):
    if id:
        with db_session:
            player = Player.get(id=id)
            if player:
                return render_template('player.html', player=player)
            else:
                abort(404)
    else:
        with db_session:
            players = Player.select()
            form = PlayerForm(csrf_enabled=False)
            return render_template('players.html', players=players, form=form)


@app.route('/players/new', methods=['POST'])
def add_player():
    form = PlayerForm(csrf_enabled=False)
    if form.validate_on_submit():
        with db_session:
            Player(**form.data)
        return redirect(url_for('players'))  # TODO: redirect to player?
    else:
        raise FbcmError(get_first_error(form))


@app.route('/teams/', defaults={'id': None})
@app.route('/teams/<id>')
def teams(id):
    if id:
        return "Team: {}".format(id)
    else:
        with db_session:
            teams = Team.select()
            form = TeamForm(csrf_enabled=False)
            return render_template('teams.html', teams=teams, form=form)


@app.route('/teams/new', methods=['POST'])
def add_team():
    form = TeamForm(csrf_enabled=False)
    if form.validate_on_submit():
        with db_session:
            Team(**form.data)
        return redirect(url_for('teams'))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/championships/', defaults={'id': None})
@app.route('/championships/<id>')
def championships(id):
    if id:
        return "Championship: {}".format(id)
    else:
        with db_session:
            championships = Championship.select()
            form = ChampionshipForm(csrf_enabled=False)
            return render_template(
                'championships.html',
                championships=championships,
                form=form
            )


@app.route('/championships/new', methods=['POST'])
def add_championship():
    form = ChampionshipForm(csrf_enabled=False)
    if form.validate_on_submit():
        with db_session:
            Championship(
                **form.data,
                points_winner=2,
                points_draw=1,
                points_loser=0
            )
        return redirect(url_for('championships'))
    else:
        raise FbcmError(get_first_error(form))


@app.errorhandler(FbcmError)
def fbcm_error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
