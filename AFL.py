from flask import Flask, request, jsonify, render_template, redirect, url_for

from model import Player, Team, Game, AFL_DB
import config
import tools

app = Flask(__name__)

db = AFL_DB(database=config.DBNAME)

@app.errorhandler(405)
def method_not_allowed(error=None):
    app.logger.warning('Method Not Allowed: ' + request.method, )

    message = {
        'status': 405,
        'message': 'Method Not Allowed: ' + request.method,
    }
    resp = jsonify(message)
    resp.status_code = 405

    return resp


@app.route('/')
def home_page():
    game = db.get_open_game()
    if not game:
        return redirect(url_for("games_get_post"))
    else:
        return redirect(url_for('games_get', timestamp=game.timestamp))

@app.route('/players',methods=['GET', 'POST'])
def players_get_post():
    if request.method == 'POST':
        name = request.form['name']
        db.create_player(name=name)

    all_players = db.get_all_players()

    return render_template('players.html', players=all_players)

@app.route('/players/<name>',methods=['GET', 'DELETE', 'PUT'])
def players_name_get_delete_put(name):
    if request.method == 'GET':
        player = db.get_player_by_name(name=name)
        return render_template('player_page.html', player=player)
    elif request.method == 'DELETE':
        return "DELETE {name}: NOT IMPLEMENTED YET ".format(name=name)
    elif request.method == 'PUT':
        player = db.create_player(name)
        return "PUT {name}: NOT IMPLEMENTED YET ".format(name=name)
    else:
        return method_not_allowed()

@app.route('/teams')
def teams_get():
    all_teams = db.get_all_teams()
    return render_template('teams.html', teams=all_teams)

@app.route('/teams/<team_id>',methods=['GET'])
def teams_name_get(team_id):
    team = db.get_team(team_id=team_id)
    return render_template('team_page.html', team=team)

@app.route('/games', methods=['GET', 'POST'])
def games_get_post():

    all_players = db.get_all_players()

    if request.method == 'POST':
        left_defense_player_name = request.form['left_defense_player_name']
        left_attack_player_name = request.form['left_attack_player_name']
        right_defense_player_name = request.form['right_defense_player_name']
        right_attack_player_name = request.form['right_attack_player_name']

        timestamp = tools.getTimestampForNow()
        team_left = db.create_team(defense_player=db.get_player_by_name(left_defense_player_name),
                                   attack_player=db.get_player_by_name(left_attack_player_name))
        team_right = db.create_team(defense_player=db.get_player_by_name(right_defense_player_name),
                                   attack_player=db.get_player_by_name(right_attack_player_name))

        print "RIGHT", team_right.summary()
        print "LEFT", team_left.summary()

        game = db.create_update_game(timestamp=timestamp, team_left=team_left, team_right=team_right)
        return redirect(url_for('games_get', timestamp=timestamp))

    else:
        all_games = db.get_all_games()
        return render_template('games.html', players=all_players, games=all_games)



@app.route('/games/<timestamp>',methods=['GET', 'PUT', 'DELETE', 'POST'])
def games_get(timestamp):
    all_players = db.get_all_players()
    game = db.get_game_by_timestamp(timestamp)
    """
    if request.method == 'GET':
        return "games_get"
    elif request.method == 'PUT':
        return "games_get"
    elif request.method == 'DELETE':
        return "games_get"
    elif request.method == 'POST':
        return "games_get"
    """
    return render_template('game.html', game=game, players=all_players)

@app.route('/games/<timestamp>/end',methods=['GET'])
def end_game(timestamp):
    # ignoring timestamp, close everything
    db._end_all_opened_games()
    return redirect(url_for('games_get', timestamp=timestamp))

@app.route('/goal/<side>',methods=['POST'])
def goal(side):
    db.goal(side=side)
    print "Received"+request.data
    return "OK"

@app.route('/is_game_on',methods=['GET'])
def is_game_on():
    game = db.get_open_game()
    if game:
        return "Yes"
    else:
        return "No"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=False, port=7008)