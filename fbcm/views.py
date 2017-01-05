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
@db_session
def players(id):
    if id:
        player = Player.get(id=id)
        if player:
            return render_template('player.html', player=player)
        else:
            abort(404)
    else:
        players = Player.select()
        form = PlayerForm(csrf_enabled=False)
        return render_template('players.html', players=players, form=form)


@app.route('/players/new', methods=['POST'])
@db_session
def add_player():
    form = PlayerForm(csrf_enabled=False)
    if form.validate_on_submit():
        Player(**form.data)
        return redirect(url_for('players'))  # TODO: redirect to player?
    else:
        raise FbcmError(get_first_error(form))


@app.route('/teams/', defaults={'id': None})
@app.route('/teams/<id>')
@db_session
def teams(id):
    if id:
        team = Team.get(id=id)
        if team:
            return render_template('team.html', team=team)
        else:
            abort(404)
    else:
        teams = Team.select()
        form = TeamForm(csrf_enabled=False)
        return render_template('teams.html', teams=teams, form=form)


@app.route('/teams/new', methods=['POST'])
@db_session
def add_team():
    form = TeamForm(csrf_enabled=False)
    if form.validate_on_submit():
        Team(**form.data)
        return redirect(url_for('teams'))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/championships/', defaults={'id': None})
@app.route('/championships/<id>')
@db_session
def championships(id):
    if id:
        return "Championship: {}".format(id)
    else:
        championships = Championship.select()
        form = ChampionshipForm(csrf_enabled=False)
        return render_template(
            'championships.html',
            championships=championships,
            form=form
        )


@app.route('/championships/new', methods=['POST'])
@db_session
def add_championship():
    form = ChampionshipForm(csrf_enabled=False)
    if form.validate_on_submit():
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
