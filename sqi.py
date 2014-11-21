import requests
import keys
from foursquare import Foursquare
import json


def get_categories():

    def push_category(category, cats, parent=None):
        """ Save category on Parse """
        categories = category.get('categories', [])
        category_dict = {
            'hash': category.get('hash'),
            'name': category.get('name'),
            'sq_id': category.get('id'),
            'icon': category.get('icon'),
        }

        cats[0] += 1
        if parent:
            category_dict.update({'parent': {
                '__type': "Pointer",
                'className': 'Category',
                'objectId': parent
            }})

        oid = requests.get('https://api.parse.com/1/classes/Category', json=category_dict, headers={
            "X-Parse-Application-Id": keys.PARSE_APP_ID,
            "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
            'Content-type': 'application/json',
        }).json()['objectId']

        for cat in categories:
            push_category(cat, parent=oid, cats=cats)

    fsq = Foursquare(client_id=keys.FOURSQUARE_CLIENT_ID,
                     client_secret=keys.FOURSQUARE_CLIENT_SECRET,
                     version=keys.FOURSQUARE_VERSION)

    categs = fsq.find_categories()
    cs = [0]
    for category in categs:
        push_category(category, cats=cs)


def search_venues():
    fsq = Foursquare(client_id=keys.FOURSQUARE_CLIENT_ID,
                     client_secret=keys.FOURSQUARE_CLIENT_SECRET,
                     version=keys.FOURSQUARE_VERSION)

    lcs = ['19.5024271,-99.1316738', '19.412084,-99.180576',
           '19.427657,-99.204116']

    for l in lcs:
        venues = fsq.find_venues(location=l, radius=1500)

        for venue in venues:
            location = venue.get('location')
            slocation = "%s, %s" % (location.get('city', 'NA'), location.get('state', 'NA'))

            categories = []
            for category in venue.get('categories'):
                u = 'https://api.parse.com/1/classes/Category'
                cat = requests.get(u, data={
                    'where': json.dumps({'sq_id': category.get('id')}),
                }, headers={
                    "X-Parse-Application-Id": keys.PARSE_APP_ID,
                    "X-Parse-REST-API-Key": keys.PARSE_REST_KEY
                })

                cats = cat.json()['results']
                for c in cats:
                    if c.get('sq_id') == category.get('id'):
                        categories.append({
                            '__type': 'Pointer',
                            'className': 'Category',
                            'objectId': c.get('objectId')
                        })
                        break

            requests.post('https://api.parse.com/1/classes/Place', json={
                'location': {
                    '__type': 'GeoPoint',
                    'latitude': location.get('lat'),
                    'longitude': location.get('lng')
                },
                'name': venue.get('name'),
                'sq_id': venue.get('id'),
                'shortLocation': slocation,
                'categories': {'__op': 'AddRelation', 'objects': categories}
            }, headers={
                "X-Parse-Application-Id": keys.PARSE_APP_ID,
                "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
                'Content-type': 'application/json',
            })

            print venue.get('name')

    return "Populated :D"


def add_attribute(columns):
    u = 'https://api.parse.com/1/classes/Attribute'
    attrs_request = requests.get(u, data={
        'limit': 500,
    }, headers={
        "X-Parse-Application-Id": keys.PARSE_APP_ID,
        "X-Parse-REST-API-Key": keys.PARSE_REST_KEY
    })

    attribute_records = attrs_request.json()['results']

    print 'Agregando a todos los registros'

    for a in attribute_records:
        columns_dict = {}
        for column in columns:
            if a.get(column) is None:
                print "Agregar columna: ", column
                columns_dict[column] = False

        uu = 'https://api.parse.com/1/classes/Attribute/%s' % a.get('objectId')
        requests.put(uu, data=json.dumps(columns_dict), headers={
            "X-Parse-Application-Id": keys.PARSE_APP_ID,
            "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
            'Content-type': 'application/json'
        })

    print "Atributos agregados"
