from flask import Flask, request, jsonify

app = Flask(__name__)

options = ["scissors", "paper", "rock", "lizard", "spock"]

wins = {
    'rock': ['scissors','lizard'],
    'paper': ['rock','spock'],
    'scissors': ['paper','lizard'],
    'lizard': ['spock','paper'],
    'spock': ['scissors','rock']
}

messages = {
    'rock_scissors': 'Rock crushes Scissors',
    'rock_lizard': 'Rock crushes Lizard',
    'paper_rock': 'Paper covers Rock',
    'paper_spock': 'Paper disproves Spock',
    'scissors_paper': 'Scissors cut Paper',
    'scissors_lizard': 'Scissors decapitate Lizard',
    'lizard_spock': 'Lizard poisons Spock',
    'lizard_paper': 'Lizard eats Paper',
    'spock_scissors': 'Spock smashes Scissors',
    'spock_rock': 'Spock vaporizes Rock'
}

@app.route("/play", methods=['POST'])
def make_play():
    content = request.get_json(silent=True) #silent returns None instead of error
    if not content:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    player = content.get("option")
    if not player:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    player = str(player).lower()
    if player not in options:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    #after checkings, request data is valid
    import random
    computer = random.choice(options)

    if player == computer:
        result = "draw"
        message = f"{player.capitalize()} draws {computer.capitalize()}"
    elif computer in wins[player]:
        result = "win"
        message = messages[f"{player}_{computer}"]
    else:
        result = "lose"
        message = messages[f"{computer}_{player}"]

    return jsonify({
        "player": player,
        "computer": computer,
        "result": result,
        "message": message
    })
    