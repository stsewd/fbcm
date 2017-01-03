from pony.orm import db_session
from flask import (
    jsonify,
    redirect,
    render_template,
    url_for
)

from . import app
from .models import FbcmError, Player
from .forms import PlayerForm


@app.route('/')
def index():
    return redirect(url_for('players'))


@app.route('/players/', defaults={'player': None})
@app.route('/players/<player>')
def players(player):
    if player:
        pass
    else:
        form = PlayerForm(csrf_enabled=False)
        return render_template('players.html', form=form)


@app.route('/players/new', methods=['POST'])
def add_player():
    form = PlayerForm(csrf_enabled=False)
    if form.validate_on_submit():
        with db_session:
            Player(**form.data)
        return redirect(url_for('players'))  # TODO: redirect to player
    else:
        raise FbcmError(list(form.errors.values())[0][0])


@app.errorhandler(FbcmError)
def fbcm_error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
