#!/usr/bin/env python
# coding: utf-8

import requests
import time
import os
import sys

from pathlib import Path

f_name='petsamo.gpx'

res_gen = requests.get('http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key=7B79EE2988A44080A37C06570F4B5EE8')
res_rank=requests.get('https://sarl.ingenium.net.au/sarl?racenr=38602')

platform=sys.platform

if platform == 'darwin':
    root=os.path.join(str(Path.home()), 'Documents')
elif sys.platform == 'win32':
    root=os.path.join('C:', 'Users', 'vitol', 'Documents', 'Sail')
else:
    sys.exit('Could not determine platform: {}'.format(platform))

f_pos=os.path.join(root, 'Boats', 'Petsamo', f_name)

rank=res_rank.text.split('Ketch | Petsamo')[0][-18:].split(' ')[0].replace('>', '')

for boat in res_gen.json():
    name=boat['boatname']
    if name=='Petsamo':
        lat=round(boat['latitude'],3)
        lon=round(boat['longitude'],3)
        print('\n---- {} --------'.format(name.upper()))
        print('pos: {}, {}'.format(lat, lon))
        print('hdg: {}'.format(round(boat['hdg'])))
        print('spd: {}'.format(round(boat['spd']*2,1)))
        print('tws: {}'.format(round(boat['tws']*2,1)))
        print('twd: {}'.format(round(boat['twd'])))
        print('twa: {}'.format(round(boat['twa'])))
        print('heel: {}'.format(round(boat['heeldegrees'])))
        print('rank: {}'.format(rank))


s='<?xml version="1.0"?>\n<gpx>\n   <wpt lat="LATITUDE" lon="LONGTITUDE">\n      <name>TIME</name>\n      <desc>track position</desc>\n   </wpt>\n</gpx>'
s=s.replace('LATITUDE', str(lat))
s=s.replace('LONGTITUDE', str(lon))
s=s.replace('TIME', time.strftime("%d-%h %H:%M"))

f=open(f_pos, 'w')
f.write(s)
f.close()
