from flask import (
    redirect,
    render_template,
    url_for,
    request,
    jsonify
)

from . import app
from . import services as srv


@app.route('/')
def index():
    return redirect(url_for('players'))


@app.route('/players/', defaults={'player': None})
@app.route('/players/<player>')
def players(player):
    if player:
        return render_template('players.html')
    else:
        return render_template('players.html')


@app.route('/players/new', methods=['POST'])
def add_player():
    id = request.form['id']
    name = request.form['name']
    lastname = request.form['lastname']
    srv.add_player(
        id=id,
        name=name,
        lastname=lastname
    )
    return redirect(url_for('players'))


@app.errorhandler(srv.FbcmError)
def fbcm_error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
