from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from .models import mongo, insert_event, get_events
from .config import Config
import pytz
import sys

app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
mongo.init_app(app)


def iso_to_utc(dt_str):
    """Convert ISO 8601 string to UTC datetime."""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).astimezone(pytz.UTC)


@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    print(f"✅ Received event: {event_type}", file=sys.stderr)
    print(f"✅ Payload: {payload}", file=sys.stderr)

    # Defensive: bail if payload is empty
    if not payload:
        print("❌ Empty payload!", file=sys.stderr)
        return jsonify({"message": "No payload"}), 400

    try:
        if event_type == "push":
            author = payload.get("pusher", {}).get("name", "unknown")
            ref = payload.get("ref", "")
            to_branch = ref.split("/")[-1] if ref else "unknown"
            head_commit = payload.get("head_commit")

            if not head_commit:
                print("⚠️ Push event has no head_commit, skipping insert.", file=sys.stderr)
                return jsonify({"message": "No head_commit"}), 200

            timestamp = iso_to_utc(head_commit.get("timestamp"))

            insert_event({
                "author": author,
                "action": "push",
                "from_branch": None,
                "to_branch": to_branch,
                "timestamp": timestamp
            })

            print(f"✅ Stored push event by {author} to {to_branch}", file=sys.stderr)

        elif event_type == "pull_request":
            pr = payload.get("pull_request", {})
            author = pr.get("user", {}).get("login", "unknown")
            from_branch = pr.get("head", {}).get("ref", "unknown")
            to_branch = pr.get("base", {}).get("ref", "unknown")
            created_at = pr.get("created_at")
            timestamp = iso_to_utc(created_at) if created_at else datetime.utcnow()

            insert_event({
                "author": author,
                "action": "pull_request",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            })

            print(f"✅ Stored PR from {from_branch} to {to_branch}", file=sys.stderr)

            if payload.get("action") == "closed" and pr.get("merged", False):
                merged_at = pr.get("merged_at")
                merge_time = iso_to_utc(merged_at) if merged_at else datetime.utcnow()

                insert_event({
                    "author": author,
                    "action": "merge",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": merge_time
                })

                print(f"✅ Stored merge: {from_branch} -> {to_branch}", file=sys.stderr)

        else:
            print(f"⚠️ Unhandled event type: {event_type}", file=sys.stderr)
            return jsonify({"message": f"Unhandled event: {event_type}"}), 400

    except Exception as e:
        print(f"❌ Exception: {e}", file=sys.stderr)
        return jsonify({"message": "Server error"}), 500

    return jsonify({"message": "Event processed"}), 200


@app.route("/events", methods=["GET"])
def events():
    """Fetch all events for UI feed."""
    try:
        events = get_events()
        result = []
        for e in events:
            e["_id"] = str(e["_id"])
            e["timestamp"] = e["timestamp"].isoformat()
            result.append(e)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error fetching events: {e}", file=sys.stderr)
        return jsonify([]), 500


@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)


if __name__ == "__main__":
    app.run()
