import webapp2
import jinja2
import os
from google.appengine.api import urlfetch
import json

userId = ""

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Home(webapp2.RequestHandler):
    def get(self):
        home_template = jinja_env.get_template('home/home.html')
        self.response.write(home_template.render())

class Filters(webapp2.RequestHandler):
    def get(self):
        filters_template = jinja_env.get_template('filters/filters.html')
        self.response.write(filters_template.render())

class RestaurantsNearby(webapp2.RequestHandler):
    def post(self):
        global userId
        userAddress = self.request.get("user_address")
        userAddress = userAddress.replace(" ", "+")

        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + userAddress + '&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'
        #url = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'

        location_response = urlfetch.fetch(url).content
        location_response_json = json.loads(location_response)
        userId = location_response_json['results'][0]['place_id'] #home id

        latitude = location_response_json['results'][0]['geometry']['location']['lat']
        longitude = location_response_json['results'][0]['geometry']['location']['lng']

        #cuisines = self.request.params.getall('cuisine')
        cuisine = self.request.get('cuisine')
        cuisine = cuisine.lower()
        user_miles = self.request.get("miles")
        miles = str(int(user_miles)*1609.34)

        api_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(latitude) + ',' + str(longitude) + '&radius=' + miles + '&type=restaurant&keyword=' + str(cuisine) + '&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'

        rest_response = urlfetch.fetch(api_url).content
        rest_response_json = json.loads(rest_response)
        #print rest_response_json

        restaurants = []
        ratings = []
        pics = []
        id = []
        for restaurant in rest_response_json['results'][0:9]:
            id.append(restaurant['place_id'])
            restaurants.append(restaurant['name'])
            ratings.append(restaurant['rating'])
            missing_photos_counter = 0
            if 'photos' in restaurant.keys():
                photo_url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=' + str(restaurant['photos'][0]['photo_reference']) + '&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'
                pics.append(photo_url)

        dict = {
            "rest_id" : id,
            "restaurant_names" : restaurants,
            "rating_keys" : ratings,
            "photo_keys" : pics
        }

        restaurants_nearby_template = jinja_env.get_template('restaurants_nearby/restaurants_nearby.html')
        self.response.write(restaurants_nearby_template.render(dict))

class Restaurant(webapp2.RequestHandler):
    def post(self):
        global userId
        user_choice = self.request.get("user_choice")
        user_choice = user_choice.replace("/", "") #restaurant id

        restaurant_url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid='+str(user_choice)+'&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'

        user_response = urlfetch.fetch(restaurant_url).content
        user_response_json = json.loads(user_response)

        restaurant_name = user_response_json['result']['name']

        name_dict = {
            "origin" : user_choice,
            "destination" : userId,
            "name" : restaurant_name
        }

        directions_url = 'https://maps.googleapis.com/maps/api/directions/json?origin=place_id:'+str(userId)+'&destination=place_id:'+str(user_choice)+'&key=AIzaSyDGnMTSopj_ZzyiNWEEM_pdb6tBCHYxEc8'

        directions_response = urlfetch.fetch(directions_url).content
        directions_response_json = json.loads(directions_response)

        result_template = jinja_env.get_template('restaurant/restaurant.html')
        self.response.write(result_template.render(name_dict))


app = webapp2.WSGIApplication(
    [
        ('/', Home),
        ('/filters', Filters),
        ('/restaurants_nearby', RestaurantsNearby),
        ('/restaurant', Restaurant),
    ],
    debug = True
)
