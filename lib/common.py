import requests
import os
from pathlib import Path
from datetime import datetime

MY_USER='Viper Vit'

DIR_HOME=str(Path.home())
DIR_SAILDATA=os.path.join(DIR_HOME, 'Documents', 'onlinesail', 'data')

API_RACES = {
    'Stardust': 'https://sarl.ingenium.net.au/racelog?racenr=38602'
}

API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key=7B79EE2988A44080A37C06570F4B5EE8'

def get_all_own_boats_json():
    return requests.get(API_OWN_BOATS).json()

def get_race_data(race):
    return requests.get(API_RACES[race]).json()['result']

def get_boat_race_data(race, user, boat):
    return get_race_data(race)[user + '-' + boat]

def timestamp():
    return datetime.now().strftime('%d/%m %H:%M')

def timeago(timestamp):
    now = datetime.fromtimestamp(datetime.now().timestamp())
    delta = (now - datetime.fromtimestamp(timestamp)).seconds
    hrs = int(delta/3600)
    mins = int(delta/60) - hrs*60
    return (hrs, mins)