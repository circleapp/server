# -*- encoding: utf-8 -*-
from flask import Flask
from flask import request
import requests
import json
from utils import valid_coords
app = Flask(__name__)


@app.route("/tree", methods=["GET"])
def build_tree():
    radius = 10
    try:
        latitude = float(request.args.get('latitude', False))
        longitude = float(request.args.get('longitude', False))
        radius = float(request.args.get('radius', 10))
    except:
        return json.dumps({
            'error': 'Faltan algunos datos o estos no son válidos.'
        }), 400

    if not valid_coords(latitude, longitude):
        return json.dumps({
            'error': 'Latitud y/o Longitud inválida'
        }), 400

    query = {
        'location': {
            '$nearSphere': {
                '__type': "GeoPoint",
                'latitude': latitude,
                'longitude': longitude
            },
            '$maxDistanceInKilometers': radius
        }
    }

    query = json.dumps(query)
    req = requests.get('https://api.parse.com/1/classes/Place', data={
        'where': query
    }, headers={
        "X-Parse-Application-Id": "pjDqEx0JZwcC6mWcycXAQ6lIWaldcGtynfLIkR0B",
        "X-Parse-REST-API-Key": "m62wRFWC1JQ2fbFoNYmAPt6nmtOrRmXeUCJY49P1"
    })

    res = req.json()

    if 'error' in res:
        return json.dumps({
            'error': res['error']
        }), 400

    #TODO: Procesar algoritmo de AI para recomendaciones
    return json.dumps(res)


if __name__ == "__main__":
    app.run()
