from flask import Flask, request, jsonify, render_template
from game import LuckyNumbersLogic

app = Flask(__name__)
game = LuckyNumbersLogic()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def get_state():
    return jsonify(game.get_state())

@app.route("/api/start", methods=["POST"])
def restart():
    global game
    game = LuckyNumbersLogic()
    return get_state()

@app.route("/api/action/<action>", methods=["POST"])
def handle_action(action):
    data = request.get_json(force=True, silent=True) or {}
    success = False

    if action == "take_deck":
        success = game.take_tile_from_deck()

    elif action == "take_table":
        index = data.get('index')
        if index is None:
            return jsonify({"error": "Не указан индекс числа"}), 400
        success = game.take_tile_from_table(index)

    elif action == "place":
        row, col = data.get('row'), data.get('col')
        if row is None or col is None:
            return jsonify({"error": "Координаты не указаны"}), 400
        success = game.place_tile(row, col)

    elif action == "pass":
        success = game.pass_tile()

    if not success:
        return jsonify({
            "error": game.message,
            "state": game.get_state()
        }), 400

    return jsonify(game.get_state())

if __name__ == "__main__":
    app.run(debug=True, port=8000)