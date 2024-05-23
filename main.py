import json
from re import error
from flask import Flask, Response, request
from songs_ranking import calculate_mfcc, rank_tracks_cosine
from threading import Lock
import sqlite3

mutex = Lock()


def validate(json_data, fields):
    if all(field in json_data for field in fields):
        return True
    return False


def mfcc():
    mutex.acquire()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    """
    Gets json with {"path": string, "id": int} of song
    """
    json_data = request.get_json()
    if not validate(json_data, ["path", "id"]):
        return Response(status=400)
    print(json_data["path"])

    vec = list(map(float, calculate_mfcc(json_data["path"])))
    float_array_str = json.dumps(vec)
    query = "INSERT INTO song_features (song_id, features) VALUES (?, ?) ON CONFLICT (song_id) DO NOTHING"
    cursor.execute(query, (json_data["id"], float_array_str))
    conn.commit()
    conn.close()
    mutex.release()

    resp = {
        "id": json_data["id"],
        "data": vec,
    }
    return resp


def radio():
    mutex.acquire()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    """
    Gets json with {"target_id": int}
    """
    json_data = request.get_json()
    if not validate(json_data, ["target_id"]):
        return Response(status=400)
    target_query = "SELECT features FROM song_features WHERE song_id=?"
    res = cursor.execute(target_query, (json_data["target_id"],))
    target_features = json.loads(res.fetchone()[0])
    other_query = "select song_id, features from song_features where song_id != ?"
    res = cursor.execute(other_query, (json_data["target_id"],))
    other_features = {}
    row = res.fetchone()
    while row != None:
        other_features[row[0]] = json.loads(row[1])
        row = res.fetchone()

    conn.commit()
    conn.close()
    mutex.release()
    ranks = rank_tracks_cosine(target_features, other_features)
    return ranks


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS song_features (
        song_id INTEGER PRIMARY KEY,
        features TEXT
    )
    """
    cursor.execute(query)
    conn.commit()


def delete_song():
    """
    Gets json with {"target_id": int}
    """
    mutex.acquire()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    json_data = request.get_json()
    if not validate(json_data, ["target_id"]):
        return Response(status=400)

    query = "DELETE FROM song_features WHERE id = ?"
    cursor.execute(query, json_data["target_id"])
    conn.commit()
    conn.close()
    mutex.release()


def main():
    init_db()
    app = Flask(__name__)
    app.add_url_rule("/mfcc", view_func=mfcc, methods=["POST"])
    app.add_url_rule("/rank_tracks", view_func=radio, methods=["POST"])
    app.run(port=6969)


if __name__ == "__main__":
    main()
