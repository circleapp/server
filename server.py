# -*- encoding: utf-8 -*-
from flask import Flask
import requests
import json
app = Flask(__name__)


@app.route("/sort")
def build_tree():
    query = {
        'location': {
            '$nearSphere': {
                '__type': "GeoPoint",
                'latitude': 34,
                'longitude': 34
            },
            '$maxDistanceInKilometers': 10
        }
    }

    #'{"location": {"$nearSphere": {"__type": "GeoPoint", "latitude": 45, "longitud": 39}}}'
    query = json.dumps(query)
    print query
    req = requests.get('https://api.parse.com/1/classes/Place', data={
        'where': query
    }, headers={
        "X-Parse-Application-Id": "pjDqEx0JZwcC6mWcycXAQ6lIWaldcGtynfLIkR0B",
        "X-Parse-REST-API-Key": "m62wRFWC1JQ2fbFoNYmAPt6nmtOrRmXeUCJY49P1"
    })

    return str(req.json())

if __name__ == "__main__":
    app.run()
