from pony.orm import db_session
from flask import (
    abort, jsonify, redirect,
    render_template, url_for,
    request
)

from . import app
from .models import (
    FbcmError, Player, Team,
    Championship, Stage, Position
)
from .forms import (
    PlayerForm,
    TeamForm,
    ChampionshipForm,
    AddPlayerToTeamForm,
    AddTeamToChampionshipForm
)


def get_first_error(form):
    if form.errors:
        return list(form.errors.values())[0][0]
    else:
        return ""


def validate_player(team, player, number):
    error = ""
    if player in team.players:
        error = "El jugador ya se encuentra registrado en el equipo."
    elif player.team:
        error = "El jugador ya pertenece a otro equipo."
    elif team.players.select(lambda player: player.number == number):
        error = "El número {} ya está ocupado.".format(number)

    if error:
        raise FbcmError(error)


def add_default_stages(championship):
    Stage(
        id=0,
        championship=championship,
        name="Primera etapa",
        num_groups=4,
        algorithm='round-robin',
        num_select=2,
        draw=True
    )

    Stage(
        id=1,
        championship=championship,
        name="Cuartos de final",
        num_groups=4,
        algorithm="first-last",
        num_select=1,
        draw=False
    )

    Stage(
        id=2,
        championship=championship,
        name="Semifinal",
        num_groups=2,
        algorithm="random",
        num_select=1,
        draw=False
    )

    Stage(
        id=3,
        championship=championship,
        name="Final",
        num_groups=1,
        algorithm="random",
        num_select=1,
        draw=False
    )


@app.route('/')
def index():
    return redirect(url_for('players'))


@app.route('/players/')
@db_session
def players():
    players = Player.select()
    form = PlayerForm()
    return render_template('players.html', players=players, form=form)


@app.route('/player/<id>/')
@db_session
def player(id):
    player = Player.get(id=id)
    if player:
        return render_template('player.html', player=player)
    else:
        abort(404)


@app.route('/player/new/', methods=['POST'])
@db_session
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        Player(**form.data)
        return redirect(url_for('players'))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/teams/')
@db_session
def teams():
    teams = Team.select()
    form = TeamForm()
    return render_template('teams.html', teams=teams, form=form)


@app.route('/team/<id>/')
@db_session
def team(id):
    team = Team.get(id=id)
    if team:
        form = AddPlayerToTeamForm()
        return render_template('team.html', team=team, form=form)
    else:
        abort(404)


@app.route('/team/<id>/addplayer/', methods=['POST'])
@db_session
def add_player_to_team(id):
    form = AddPlayerToTeamForm()
    if form.validate_on_submit():
        player_id = form.player_id.data
        number = form.number.data
        position = form.position.data

        team = Team[id]
        player = Player[player_id]
        validate_player(team, player, number)
        player.set(
            number=number,
            position=Position.get(id=position),
            team=team
        )
        return redirect(url_for('teams', id=id))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/team/new/', methods=['POST'])
@db_session
def add_team():
    form = TeamForm()
    if form.validate_on_submit():
        Team(**form.data)
        return redirect(url_for('teams'))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/championships/')
@db_session
def championships():
    championships = Championship.select()
    form = ChampionshipForm()
    return render_template(
        'championships.html',
        championships=championships,
        form=form
    )


@app.route('/championship/<id>/')
@db_session
def championship(id):
    championship = Championship.get(id=id)
    if championship:
        form = AddTeamToChampionshipForm()
        return render_template(
            'championship.html',
            championship=championship,
            form=form
        )
    else:
        abort(404)


@app.route('/championship/<id>/addteam/', methods=['POST'])
@db_session
def add_team_to_championship(id):
    form = AddTeamToChampionshipForm()
    if form.validate_on_submit():
        team_name = form.team_name.data

        championship = Championship[id]
        team = Team.get(name=team_name)

        if championship.teams.select(lambda teamc: teamc.team == team):
            raise FbcmError(
                "El equipo ya se encuentra registrado en el campeonato."
            )

        championship.teams.create(team=team)
        return redirect(url_for('championships', id=id))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/championship/new/', methods=['POST'])
@db_session
def add_championship():
    form = ChampionshipForm()
    if form.validate_on_submit():
        championship = Championship(
            **form.data,
            points_winner=2,
            points_draw=1,
            points_loser=0
        )
        add_default_stages(championship)
        return redirect(url_for('championships'))
    else:
        raise FbcmError(get_first_error(form))


@app.route('/championship/<championship_id>/stages/', methods=['GET'])
@db_session
def stages(championship_id):
    stage_id = int(request.args.get('stage', '0'))
    group = int(request.args.get('group', '1'))

    championship = Championship.get(id=championship_id)
    if not championship:
        abort(404)

    stage = championship.stages.select(
        lambda stage: stage.id == stage_id
    )
    if not stage:
        abort(404)
    stage = stage[:1][0]

    if not (0 < group <= stage.num_groups):
        abort(404)

    return render_template(
        "stage.html",
        stage=stage,
        group=group,
        stages=championship.stages.select().order_by(
            lambda stage: stage.id
        )
    )


@app.route(
    '/championship/<championship_id>/stage/<stage_id>/start'
)
@db_session
def start_stage(championship_id, stage_id):
    stage = Stage.get(id=stage_id)
    if not stage or not stage.matches.is_empty():
        abort(404)
    stage.create_matches()
    return redirect(url_for('stages', championship_id=championship_id))


@app.errorhandler(FbcmError)
def fbcm_error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
