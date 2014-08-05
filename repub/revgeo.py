#!/usr/bin/env python

# JPM

try:
    import json
except ImportError:
    import simplejson as json

from urllib import urlencode
from urllib2 import urlopen

class ReverseGeo(object):
    """
    Reverse geocoder using the MapQuest Open Platform Web Service.
    """

    def __init__(self):
        """Initialize reverse geocoder; no API key is required by the
           Nomatim-based platform"""

        self.url = "http://open.mapquestapi.com/nominatim/v1/reverse?format=json&addressdetails=1&%s"
    
    
    def parse_json(self, data):
        try:
            data = json.loads(data)
        except:
            data = {}

        return data

    def reverse(self, lat, lon):

        params = { 'lat': lat, 'lon' : lon }

        url = self.url % urlencode(params)

        data = urlopen(url)
        response = data.read()

        return self.parse_json(response)
