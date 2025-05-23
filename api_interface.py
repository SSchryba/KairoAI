from flask import Flask, request, jsonify
from memory import Memory
from decision_engine import DecisionEngine

@app.route("/api/memory", methods=["GET"])
def get_memory():
    return jsonify({"memory": memory.recall()})

app = Flask(__name__)

memory = Memory()
engine = DecisionEngine(memory)

@app.route("/api/respond", methods=["POST"])
def respond():
    data = request.json
    input_text = data.get("input", "")
    response = engine.process(input_text)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
