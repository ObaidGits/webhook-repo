from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from .models import mongo, insert_event, get_events
from .config import Config
import pytz
import logging

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

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

    logger.info(f"Webhook received | Event: {event_type}")

    if not payload:
        logger.warning("Webhook called with empty payload.")
        return jsonify({"message": "No payload"}), 400

    try:
        if event_type == "push":
            author = payload.get("pusher", {}).get("name", "unknown")
            ref = payload.get("ref", "")
            to_branch = ref.split("/")[-1] if ref else "unknown"
            head_commit = payload.get("head_commit")

            if not head_commit:
                logger.warning("Push event missing head_commit.")
                return jsonify({"message": "No head_commit"}), 200

            timestamp = iso_to_utc(head_commit.get("timestamp"))

            insert_event({
                "author": author,
                "action": "push",
                "from_branch": None,
                "to_branch": to_branch,
                "timestamp": timestamp
            })

            logger.info(f"Stored PUSH | Author: {author} | Branch: {to_branch}")

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

            logger.info(f"Stored PR | {from_branch} → {to_branch} | Author: {author}")

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
                logger.info(f"Stored MERGE | {from_branch} → {to_branch} | Author: {author}")

        else:
            logger.warning(f"Unhandled GitHub event type: {event_type}")
            return jsonify({"message": f"Unhandled event: {event_type}"}), 400

    except Exception as e:
        logger.error(f"Exception processing webhook: {e}", exc_info=True)
        return jsonify({"message": "Server error"}), 500

    return jsonify({"message": "Event processed"}), 200

@app.route("/events", methods=["GET"])
def events():
    after = request.args.get("after")
    before = request.args.get("before")
    limit = int(request.args.get("limit", 10))

    after_dt = None
    before_dt = None

    try:
        if after:
            after_dt = datetime.fromisoformat(after)
        if before:
            before_dt = datetime.fromisoformat(before)
    except ValueError:
        logger.warning(f"Invalid date format | after: {after} | before: {before}")
        return jsonify({"error": "Invalid date format"}), 400

    docs = get_events(after=after_dt, before=before_dt, limit=limit + 1)
    has_more = len(docs) > limit

    if has_more:
        docs = docs[:limit]

    logger.info(f"Fetched {len(docs)} events | after={after} | before={before} | has_more={has_more}")

    result = []
    for doc in docs:
        doc["timestamp"] = doc["timestamp"].isoformat()
        result.append(doc)

    return jsonify({"events": result, "hasMore": has_more})

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)

if __name__ == "__main__":
    app.run()
