from pony.orm import db_session, select
from flask import (
    abort, jsonify, redirect,
    render_template, url_for,
    request
)

from . import app
from .models import (
    FbcmError, Player, Team,
    Championship, Stage, Position,
    Match
)
from .forms import (
    GoalForm,
    TeamForm,
    PlayerForm,
    ChampionshipForm,
    AddPlayerToTeamForm,
    AddTeamToChampionshipForm
)

from .tools import (
    add_default_stages,
    get_first_error,
    validate_player,
    get_match
)


@app.route('/')
def index():
    return redirect(url_for('players'))


@app.route('/players/')
@db_session
def players():
    players = Player.select()
    form = PlayerForm()
    return render_template(
        'players.html',
        players=players,
        form=form
    )


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
    return render_template(
        'teams.html',
        teams=Team.select(),
        form=TeamForm()
    )


@app.route('/team/<id>/')
@db_session
def team(id):
    team = Team.get(id=id)
    if team:
        return render_template(
            'team.html',
            team=team,
            form=AddPlayerToTeamForm()
        )
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
            position=Position[position],
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
    return render_template(
        'championships.html',
        championships=Championship.select(),
        form=ChampionshipForm()
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

        if championship.teams.select(lambda tc: tc.team == team):
            raise FbcmError(
                "El equipo ya se encuentra registrado en el campeonato."
            )
        else:
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

    stage = Stage.get(
        id=stage_id,
        championship=championship_id
    )
    if not stage:
        abort(404)

    if not (0 < group <= stage.num_groups):
        abort(404)

    return render_template(
        "stage.html",
        stage=stage,
        group=group,
        stages=Stage.select(
            lambda s: s.championship.id == championship_id
        ).prefetch(
            Championship
        ).order_by(
            lambda stage: stage.id
        )
    )


@app.route(
    '/championship/<championship_id>/stage/<stage_id>/start/'
)
@db_session
def start_stage(championship_id, stage_id):
    stage = Stage.get(id=stage_id, championship=championship_id)
    if not stage or not stage.matches.is_empty():
        abort(404)
    stage.create_matches()
    return redirect(url_for('stages', championship_id=championship_id))


@app.route(
    '/championship/<championship>/stage/<stage>/' +
    'match/<group>/<round>/<match>/'
)
@db_session
def match(championship, stage, group, round, match):
    match = Match.get(
        stage=Stage[stage, championship],
        group=group,
        round=round,
        id=match
    )
    if not match:
        return abort(404)
    form = GoalForm(match)
    return render_template('match.html', form=form, match=match)


@app.route(
    '/championship/<championship>/' +
    'stage/<stage>/match/<group>/<round>/<match>/goal/',
    methods=['POST']
)
@db_session
def goal(championship, stage, group, round, match):
    player = request.form['player']
    team = request.form['team']
    team_match = select(
        tm
        for c in Championship
        for s in c.stages
        for m in s.matches
        for tm in m.team_matches
        if (c.id == championship and
            s.id == stage and
            m.id == match and
            m.group == group and
            m.round == round and
            tm.team.team == Team[team])
    ).first()
    team_match.goals.create(
        player=player
    )

    return redirect(url_for(
        'match',
        championship=championship,
        stage=stage,
        group=group,
        round=round,
        match=match
    ))


@app.route(
    '/championship/<championship>/' +
    'stage/<stage>/match/<group>/<round>/<match>/start/',
    methods=['POST']
)
@db_session
def start_match(championship, stage, group, round, match):
    match_ = get_match(championship, stage, group, round, match)
    match_.state = 'started'

    return redirect(url_for(
        'match',
        championship=championship,
        stage=stage,
        group=group,
        round=round,
        match=match
    ))


@app.route(
    '/championship/<championship>/' +
    'stage/<stage>/match/<group>/<round>/<match>/finish/',
    methods=['POST']
)
@db_session
def finish_match(championship, stage, group, round, match):
    match_ = get_match(championship, stage, group, round, match)
    match_.state = 'finished'

    return redirect(url_for(
        'match',
        championship=championship,
        stage=stage,
        group=group,
        round=round,
        match=match
    ))


@app.route('/championship/<championship>/top/')
@db_session
def top(championship):
    ch = Championship.get(id=championship)
    if not ch:
        abort(404)
    return render_template('top-players.html', championship=ch)


@app.errorhandler(FbcmError)
def fbcm_error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
