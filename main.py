from re import error
from flask import Flask, Response, request
from songs_ranking import calculate_mfcc


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
    resp = {
        "id": json_data["id"],
        "data": vec,
    }
    return resp


def radio():
    """
    Gets json with {"target_id": int}
    """
    return "Unimplemented"


def main():
    app = Flask(__name__)
    app.add_url_rule("/mfcc", view_func=mfcc, methods=["POST"])
    app.add_url_rule("/rank_tracks", view_func=radio, methods=["POST"])
    app.run(port=6969)


if __name__ == "__main__":
    main()
