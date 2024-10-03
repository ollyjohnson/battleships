"""Handles requests to and from the server for the web interface version of the battleships game"""
import logging
from flask import Flask, request, render_template, jsonify
from components import create_battleships, initialise_board, place_battleships
from game_engine import attack
from mp_game_engine import generate_attack

app = Flask(__name__)

players = {
    "player1": {"Board": None, "Ships": None, "Attacks": []},
    "robot": {"Board": None, "Ships": None, "Attacks": [], "Hits": []},
}

setup = {"board_size": 8, "difficulty": "hard"}

@app.route('/placement', methods=["GET", "POST"])
def placement_interface():
    """Handles the placement interface for battleships at the /placement url.

    GET: Loads the empty board for the player to place their ships.
    POST: Receives player's ship placement data and initialises boards for player and the ai.

    returns: JSON response indicating successful reception."""
    global players,setup
    ships = create_battleships()

    if request.method == "GET":
        return render_template('placement.html', ships=ships, board_size=setup["board_size"])

    if request.method == "POST":
        player_ships = request.get_json()

        players["player1"]["Board"] = place_battleships(
            initialise_board(size=setup["board_size"]), ships, algorithm="custom",
            custom_placement=player_ships)
        players["player1"]["Ships"] = create_battleships()
        players["player1"]["Attacks"] = []

        players["robot"]["Board"] = place_battleships(
            initialise_board(size=setup["board_size"]), ships, algorithm="random")
        players["robot"]["Ships"] = create_battleships()
        players["robot"]["Attacks"] = []
        players["robot"]["Hits"] = []
        logging.info("Boards initialised")
        return jsonify({'message': 'Received'})

    return

@app.route('/', methods=["GET"])
def root():
    """Renders the main game interface at the root / url."""
    global players
    player1_board = players["player1"]["Board"]
    return render_template('main.html', player_board=player1_board)

@app.route('/attack', methods=["GET"])
def process_attack():
    """Handles the attack process for both the user and ai.

    return: JSON response with the players hit information and the
    next attack coordinates for the ai."""
    global players,setup
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))

    if (x, y) in players["player1"]["Attacks"]:
        logging.warning("Repeated attack coordinates: %s, %s", x, y)
        return None

    player_hit, players["robot"]["Board"], players["robot"]["Ships"] = attack(
        (x, y), players["robot"]["Board"], players["robot"]["Ships"])
    logging.info("Player attack: %s, %s", x, y)
    ai_attack_coordinates = generate_attack(
        players["robot"]["Attacks"], setup["board_size"], difficulty=setup["difficulty"],
        previous_hits=players["robot"]["Hits"])
    ai_hit, players["player1"]["Board"], players["player1"]["Ships"] = attack(
        ai_attack_coordinates, players["player1"]["Board"],
        players["player1"]["Ships"])
    logging.info("AI attack: %s", ai_attack_coordinates)
    players["player1"]["Attacks"].append((x, y))
    players["robot"]["Attacks"].append(ai_attack_coordinates)
    players["robot"]["Hits"].append(ai_hit)

    if sum(players["robot"]["Ships"].values()) == 0:
        logging.info("Game over, Player wins")
        return jsonify({
            'hit': player_hit,
            'AI_Turn': ai_attack_coordinates,
            'finished': 'Game Over Player wins'})
    elif sum(players["player1"]["Ships"].values()) == 0:
        logging.info("Game over, Robot wins")
        return jsonify({
            'hit': player_hit,
            'AI_Turn': ai_attack_coordinates,
            'finished': 'Game Over Robot wins'})
    else:
        return jsonify({'hit': player_hit, 'AI_Turn': ai_attack_coordinates})

if __name__ == '__main__':
    app.template_folder = "templates"
    app.run(debug=True)
