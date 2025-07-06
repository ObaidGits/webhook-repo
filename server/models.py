from flask_pymongo import PyMongo
import logging

# Logger for DB layer
logger = logging.getLogger(__name__)

mongo = PyMongo()

def insert_event(event):
    try:
        mongo.db.events.insert_one(event)
        logger.info(f"[DB] Inserted event: {event['action']} by {event['author']}")
    except Exception as e:
        logger.error(f"[DB] Failed to insert event: {e}", exc_info=True)

def get_events(after=None, before=None, limit=20):
    query = {}
    if after:
        query['timestamp'] = {'$gt': after}
    if before:
        query['timestamp'] = {'$lt': before}

    logger.info(f"[DB] Query: {query} | Limit: {limit}")

    try:
        results = list(
            mongo.db.events
            .find(query, {"_id": 0})  # 👈 This projection excludes _id at the DB level!
            .sort('timestamp', -1)
            .limit(limit)
        )
        logger.info(f"[DB] Returned {len(results)} events")
        return results
    except Exception as e:
        logger.error(f"[DB] Failed to fetch events: {e}", exc_info=True)
        return []
