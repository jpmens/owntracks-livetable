#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import ssl
import time
import logging
import json
import sys
import os
import re
import gdbm
from revgeo import ReverseGeo
from weather import OpenWeatherMAP
from datetime import datetime

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'

devices = {}
vehicles = {}

db = gdbm.open("nominatimcache.gdbm", "cs", 0644)
weatherdb = gdbm.open("weathermapcache.gdbm", "cs", 0644)

# 3rd decimal place (0.001) is 111m 
# http://gis.stackexchange.com/questions/8650/how-to-measure-the-accuracy-of-latitude-and-longitude

def on_connect(mosq, userdata, rc):
    mqttc.subscribe("owntracks/+/+/status", 0)
    mqttc.subscribe("owntracks/+/+", 0)

def on_publish(mosq, userdata, mid):
    # print("mid: "+str(mid))
    pass

def shortenize(nominatim):
    ''' data  contains nominatim address details in JSON '''

    disp = ''

    data = nominatim['address']

    if 'road' in data:
        disp = disp + data['road'] + " "

    if 'pedestrian' in data:
        disp = disp + data['pedestrian'] + " "
    if 'information' in data:
        disp = disp + data['information'] + " "

    if 'house_number' in data:
        disp = disp + data['house_number'] + " "

    # house, building, subway, golf_course, bus_stop, parking

    if 'postcode' in data:
        disp = disp + data['postcode'] + " "

    if 'city' in data:
        disp = disp + data['city'] + " "
    else:
        if 'town' in data:
            disp = disp + data['town'] + " "
        else:
            if 'village' in data:
                disp = disp + data['village'] + " "

    if 'county' in data:
        disp = disp + '(' + data['county'] + ") "

    if 'country_code' in data:
        disp = disp + data['country_code'].upper()

    disp = disp.strip()
    return disp

def weather(lat, lon):
    ''' Given lat, lon, return current weather, either from cache
        or from weathermap '''

    short_lat = round(float(lat), 3)
    short_lon = round(float(lon), 3)

    key = "%s,%s-%s" % (short_lat, short_lon,
        time.strftime('%F-%H', time.localtime(time.time())))

    weathertemp = 'unknown'
    if key in weatherdb:
        weathertemp = json.loads(weatherdb[key])
    else:
        weather = OpenWeatherMAP()

        try:
            w = weather.weather(short_lat, short_lon)
            weathertemp = dict(weather=w['current'], temp=w['celsius'])
            weatherdb[key] = json.dumps(weathertemp)
        except:
            pass

    # print "--------> ", key, weathertemp
    return weathertemp

def revgeo(lat, lon):
    ''' Given lat, lon, return reverse geo location, either from cache
        or from nominatim '''

    short_lat = round(float(lat), 3)
    short_lon = round(float(lon), 3)
    key = "%s,%s" % (short_lat, short_lon)

    if key in db:
        location = json.loads(db[key])
    else:
        nominatim = ReverseGeo()
        location = nominatim.reverse(short_lat, short_lon)
        if type(location) == dict and 'error' in location:
            location = location['error']
            return location

        location = shortenize(location)
        db[key] = json.dumps(location)

    return location

def repub(mosq, dev, devdata):

    if 'lat' not in devdata or 'lon' not in devdata:
        return

    car = '00'
    if dev in vehicles:
        car = vehicles[dev]

    topic = re.sub('^owntracks/', 't/', dev)

    devdata['geo'] = revgeo(devdata.get('lat', 0), devdata.get('lon', 0))

    weathertemp = weather(devdata.get('lat', 0), devdata.get('lon', 0))
    devdata['weather'] = weathertemp.get('weather', 'unknown')
    devdata['temp'] = weathertemp.get('temp', '?')
    devdata['car'] = car


    new_payload = json.dumps(devdata)
    mosq.publish(topic, new_payload, qos=0, retain=False)


def on_status(mosq, userdata, msg):
    # print "$$$$$$$- STATUS %s (qos=%s, r=%s) %s" % (msg.topic, str(msg.qos), msg.retain, str(msg.payload))

    dev = str(msg.topic)
    if dev.endswith('/status'):
        dev = dev[:-7]

    if dev in devices:
        status = -1
        try:
            status = int(msg.payload)
        except:
            pass
        devices[dev].update(dict(status=status))
    else:
        devices[dev] = dict(status=int(msg.payload))

    repub(mosq, dev, devices[dev])
    
def on_message(mosq, userdata, msg):
    # print "%s (qos=%s, r=%s) %s" % (msg.topic, str(msg.qos), msg.retain, str(msg.payload))

    topic = str(msg.topic);
    payload = str(msg.payload)

    try:
        data = json.loads(payload)
    except:
        return

    if '_type' not in data:
        return
    if data['_type'] != 'location':
        return

    dev = topic

    if not 'tst' in data:
        data['tst'] = int(time.time())

    newdata = {
        'lat' : float(data.get('lat', 0)),
        'lon' : float(data.get('lon', 0)),
        'cog' : int(float(data.get('cog', 0))), 
        'vel' : int(float(data.get('vel', 0))),
        'alt' : int(float(data.get('alt', 0))),
        'tstamp' : time.strftime('%d/%H:%M:%S', time.localtime(int(data['tst']))),
    }

    try:
        devices[dev].update(newdata)
    except KeyError:
        devices[dev] = newdata


    # new_payload = json.dumps(data)

    repub(mosq, dev, devices[dev])

clientID = "tablerepub-%d" % os.getpid()

mqttc = paho.Client(clientID, clean_session=True, userdata=None)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

mqttc.message_callback_add("owntracks/+/+/status", on_status)

f = open('vehicles.json')
vehicles = json.loads(f.read())
f.close()

mqttc.connect("172.16.153.122", 1883, 60)

while True:
    try:
        mqttc.loop_forever()
        time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(0)

