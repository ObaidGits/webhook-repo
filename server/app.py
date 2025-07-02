from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from models import mongo, insert_event, get_events
from config import Config
import pytz

app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
mongo.init_app(app)

@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    # UTC timestamp parsing helper
    def iso_to_utc(dt_str):
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).astimezone(pytz.UTC)

    if event_type == "push":
        author = payload.get("pusher", {}).get("name")
        to_branch = payload["ref"].split("/")[-1]
        timestamp = iso_to_utc(payload["head_commit"]["timestamp"])
        insert_event({
            "author": author,
            "action": "push",
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        author = pr.get("user", {}).get("login")
        from_branch = pr.get("head", {}).get("ref")
        to_branch = pr.get("base", {}).get("ref")
        timestamp = iso_to_utc(pr.get("created_at"))
        insert_event({
            "author": author,
            "action": "pull_request",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

        # Bonus: If PR closed & merged → treat as merge event
        if payload.get("action") == "closed" and pr.get("merged", False):
            merge_time = iso_to_utc(pr.get("merged_at"))
            insert_event({
                "author": author,
                "action": "merge",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": merge_time
            })

    else:
        return jsonify({"message": f"Unhandled event: {event_type}"}), 400

    return jsonify({"message": "Event processed"}), 200

@app.route("/events", methods=["GET"])
def events():
    """
    API to fetch all events. Frontend polls this every 15s.
    """
    events = get_events()
    result = []
    for e in events:
        e["_id"] = str(e["_id"])
        e["timestamp"] = e["timestamp"].isoformat()
        result.append(e)
    return jsonify(result)

# Serve static frontend
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)

if __name__ == "__main__":
    app.run()
