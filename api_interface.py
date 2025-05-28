from flask import Flask, request, jsonify
from memory import Memory
from decision_engine import DecisionEngine

app = Flask(__name__)

# Initialize core components
memory = Memory()
engine = DecisionEngine(memory)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "kairo-ai"})

@app.route("/api/memory", methods=["GET"])
def get_memory():
    try:
        return jsonify({"memory": memory.recall()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/respond", methods=["POST"])
def respond():
    try:
        data = request.json
        if not data or "input" not in data:
            return jsonify({"error": "Missing input field"}), 400
            
        input_text = data.get("input", "")
        response = engine.process(input_text)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This block is only used when running directly with python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
