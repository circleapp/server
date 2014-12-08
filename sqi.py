import requests
import keys
from foursquare import Foursquare
import json
import urllib


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


def get_pix():

    fsq = Foursquare(client_id=keys.FOURSQUARE_CLIENT_ID,
                     client_secret=keys.FOURSQUARE_CLIENT_SECRET,
                     version=keys.FOURSQUARE_VERSION)

    u = 'https://api.parse.com/1/classes/Place'
    places_req = requests.get(u, data={
        'limit': 500
    }, headers={
        "X-Parse-Application-Id": keys.PARSE_APP_ID,
        "X-Parse-REST-API-Key": keys.PARSE_REST_KEY
    })

    places = places_req.json().get('results', [])
    for place in places:
        print 'Obteniendo fotos para >> %s <<' % place.get('name')
        sq_id = place.get('sq_id')
        place_parse_id = place.get('objectId')
        pix_objects = []
        if sq_id:
            pix = fsq.venues_pix(sq_id)
            pix_len = len(pix)
            # for pic in pix:
            for i in xrange(0, 7):
                if i >= pix_len:
                    break

                pic = pix[i]
                if pic.get('visibility') == 'public':
                    dimen = "%sx%s" % (pic.get('height'), pic.get('width'))
                    url = "%s%s%s" % (pic.get('prefix'), dimen, pic.get('suffix'))
                    pic_request = requests.get(url)

                    upload_url = 'https://api.parse.com/1/files/' + pic.get('suffix')[1:]
                    upload_request = requests.post(upload_url, data=pic_request.content, headers={
                        "X-Parse-Application-Id": keys.PARSE_APP_ID,
                        "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
                        'Content-type': 'image/jpeg'
                    })
                    uploaded_filename = upload_request.json()['name']

                    pic_parse_url = 'https://api.parse.com/1/classes/Pic'
                    pic_parse_request = requests.post(pic_parse_url, data=json.dumps({
                        'image': {
                            '__type': 'File',
                            'name': uploaded_filename
                        }
                    }), headers={
                        "X-Parse-Application-Id": keys.PARSE_APP_ID,
                        "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
                    })

                    pic_objectId = pic_parse_request.json().get('objectId')

                    if pic_objectId:
                        pix_objects.append({
                            '__type': 'Pointer',
                            'className': 'Pic',
                            'objectId': pic_objectId
                        })
        else:
            print "\tNo hay fotos"
            continue

        if pix_objects:
            print '\tActualizando fotos'
            place_parse_url = 'https://api.parse.com/1/classes/Place/' + place_parse_id
            place_pix_request = requests.put(place_parse_url, data=json.dumps({
                'pix': {'__op': 'AddRelation', 'objects': pix_objects}
            }), headers={
                "X-Parse-Application-Id": keys.PARSE_APP_ID,
                "X-Parse-REST-API-Key": keys.PARSE_REST_KEY,
            })
            if place_pix_request.json().get('updatedAt'):
                print '\t\tActualizado.', "((%s))" % place_parse_id
            # print pix_objects, place_parse_id, place_parse_urlx


def testings():
    u = 'https://api.parse.com/1/classes/Place'
    cat = requests.get(u, data={
        'where': json.dumps({
            '$relatedTo': {
                'object': {
                    '__type': 'Pointer',
                    'className': '_User',
                    'objectId': 'E4oafmmqyP'
                },
                'key': 'favs'
            }
        })
    }, headers={
        "X-Parse-Application-Id": keys.PARSE_APP_ID,
        "X-Parse-REST-API-Key": keys.PARSE_REST_KEY
    })

    print cat.json()
