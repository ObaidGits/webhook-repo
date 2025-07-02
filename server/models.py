from flask_pymongo import PyMongo

mongo = PyMongo()

def insert_event(event):
    """
    Insert a new event to the 'events' collection.
    """
    mongo.db.events.insert_one(event)

def get_events(last_seen=None):
    """
    Return events sorted by timestamp desc.
    If 'last_seen' is given, return only newer events.
    """
    query = {}
    if last_seen:
        query = {'timestamp': {'$gt': last_seen}}
    return list(mongo.db.events.find(query).sort('timestamp', -1))
