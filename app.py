from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "🚀 Flask server is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    print(payload)  # just log for now
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run()
