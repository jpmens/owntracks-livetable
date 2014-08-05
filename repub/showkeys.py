#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import gdbm

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'

db = gdbm.open("nominatimcache.gdbm", "ru", 0644)

k = db.firstkey()
while k != None:
    print k, db[k]
    k = db.nextkey(k)
