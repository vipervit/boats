#!/usr/bin/env python
# coding: utf-8

import requests
response = requests.get('http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key=7B79EE2988A44080A37C06570F4B5EE8')

for boat in response.json():
    print('\n---- {} --------'.format(boat['boatname'].upper()))
    print('pos: {}, {}'.format(round(boat['latitude'],3), round(boat['longitude'],3)))
    print('hdg: {}'.format(round(boat['hdg'])))
    print('spd: {}'.format(round(boat['spd'],1)))
    print('tws: {}'.format(round(boat['tws'],1)))
    print('twd: {}'.format(round(boat['twd'])))

