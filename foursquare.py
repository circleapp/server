import requests
from unidecode import unidecode
import hashlib


class Foursquare(object):
    API_URL = "https://api.foursquare.com/v2"
    CATEGORIES_URL = API_URL + "/venues/categories/"
    SEARCH_URL = API_URL + "/venues/search/"

    def __init__(self, client_id, client_secret, version, locale='es'):
        self.ACCES_PARAMS = "?client_id=%s&client_secret=%s&v=%s&locale=%s" % (
            client_id, client_secret, version, locale)

        self.CATEGORIES_URL += self.ACCES_PARAMS
        self.SEARCH_URL += self.ACCES_PARAMS

    def find_categories(self):
        engine = Foursquare.Category()
        return engine.get_categories(url=self.CATEGORIES_URL)

    def find_venues(self, location, radius=1):
        engine = Foursquare.Venue(sq=self)
        return engine.search_venues(location, radius)

    def venues_pix(self, venue_id):
        engine = Foursquare.Venue(sq=self)
        return engine.get_photos(venue_id)

    class Category(object):
        def get_category_info(self, category):
            name = category.get('shortName')
            plain_name = unidecode(name).replace(' ', '').lower()
            hash_name = hashlib.sha1(plain_name).hexdigest()
            return {
                'categories': self.search_categories(category),
                'icon': category.get('icon'),
                'id': category.get('id'),
                'hash': hash_name,
                'name': name
            }

        def search_categories(self, category):
            categories = []
            if 'categories' in category:
                for category in category['categories']:
                    categories.append(self.get_category_info(category))
                return categories
            else:
                return categories

        def print_category(self, category, sub=False, tabs=0):
            if sub:
                print "\t" * tabs,
            print category.get('name')

            categories = category.get('categories', [])
            tabs += 1 if categories else 0

            for cat in categories:
                self.print_category(cat, sub=True, tabs=tabs)

        def get_categories(self, url):
            #TODO: Manejar errores de la API
            categories_request = requests.get(url)
            categories = categories_request.json()['response']['categories']

            categories_ = []
            for category in categories:
                categories_.append(self.get_category_info(category))

            return categories_
            print "Categorias listas :D"
            # for cat in categories_:
            #     self.print_category(cat)

    class Venue(object):

        def __init__(self, sq):
            self.sq = sq

        def get_venue_info(self, venue):
            return {
                'id': venue.get('id'),
                'name': venue.get('name'),
                'location': venue.get('location'),
                'categories': venue.get('categories')
            }

        def get_tip_info(tip):
            return {
                'id': tip.get('id'),
                'text': tip.get('text')
            }

        def get_photos(self, venue_id):
            venue_pix_url = "%s/venues/%s/photos/%s/" % (self.sq.API_URL,
                                                         venue_id,
                                                         self.sq.ACCES_PARAMS)

            pix_request = requests.get(venue_pix_url)
            pix = pix_request.json()['response']['photos']['items']
            return pix

        def get_tips(self, venue_id):
            venue_tips_url = "%s/venues/%s/tips/%s/" % (self.sq.API_URL,
                                                        venue_id,
                                                        self.sq.ACCES_PARAMS)
            print venue_tips_url
            # tips_request = requests.get(venue_tips_url)
            # print tips_request.json()

        def search_venues(self, location, radius):
            sparams = "&intent=browse&radius=%s&ll=%s&limit=50" % (radius, location)
            u = "%s%s" % (self.sq.SEARCH_URL, sparams)
            venues_request = requests.get(u)
            venues = venues_request.json()['response']['venues']
            vs = []
            for venue in venues:
                vs.append(self.get_venue_info(venue))
                # self.get_tips(venue_id=v.get('id'))
            return vs
