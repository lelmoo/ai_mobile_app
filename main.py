import json
from re import error
from flask import Flask, Response, request
from songs_ranking import calculate_mfcc, rank_tracks_cosine
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def validate(json_data, fields):
    if all(field in json_data for field in fields):
        return True
    return False


def mfcc():
    """
    Gets json with {"path": string, "id": int} of song
    """
    json_data = request.get_json()
    if not validate(json_data, ["path", "id"]):
        return Response(status=400)
    print(json_data["path"])

    vec = list(map(float, calculate_mfcc(json_data["path"])))
    float_array_str = json.dumps(vec)
    query = "INSERT INTO song_features (song_id, features) VALUES (?, ?)"
    cursor.execute(query, (json_data["id"], float_array_str))
    conn.commit()

    resp = {
        "id": json_data["id"],
        "data": vec,
    }
    return resp


def radio():
    """
    Gets json with {"target_id": int}
    """
    json_data = request.get_json()
    if not validate(json_data, ["target_id"]):
        return Response(status=400)
    # rank_tracks_cosine(json_data["target_id"], ) TODO!!!
    return "Unimplemented"

def init_db():
    query = """
    CREATE TABLE IF NOT EXISTS song_features (
        song_id INTEGER PRIMARY KEY,
        features TEXT
    )
    """
    cursor.execute(query)
    conn.commit()

def main():
    init_db()
    app = Flask(__name__)
    app.add_url_rule("/mfcc", view_func=mfcc, methods=["POST"])
    app.add_url_rule("/rank_tracks", view_func=radio, methods=["POST"])
    app.run(port=6969)


if __name__ == "__main__":
    main()
