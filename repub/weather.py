#!/usr/bin/env python

# JPM

try:
    import json
except ImportError:
    import simplejson as json

from urllib import urlencode
from urllib2 import urlopen

class OpenWeatherMAP(object):
    """
    Obtain weather and temperature for lat/lon from OpenWeatherMap.org
    """

    def __init__(self):

        self.url = 'http://api.openweathermap.org/data/2.5/weather?%s'

    def weather(self, lat, lon):
        params = { 'lat': lat, 'lon' : lon }
        celsius = None
        current = None

        url = self.url % urlencode(params)

        data = urlopen(url)
        response = data.read()
        weather_data = self.parse_json(response)

        if 'main' in weather_data and 'temp' in weather_data['main']:
            celsius = "%0.1f" % (float(weather_data['main']['temp']) - 273.15)

        if 'weather' in weather_data:
            if 'main' in weather_data['weather'][0]:
                current = weather_data['weather'][0]['main']


        item = {
            'current'   : current,
            'celsius'   : celsius,
            'blob'      : weather_data
        }
        return item
    
    def parse_json(self, data):
        try:
            data = json.loads(data)
        except:
            data = {}

        return data
