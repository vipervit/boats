import requests

API_RACES = {
    'Stardust': 'https://sarl.ingenium.net.au/racelog?racenr=38602'
}

def get_boat_data(boat):
    url='http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key=7B79EE2988A44080A37C06570F4B5EE8'
    response=requests.get(url)
    for data in response.json():
        if data['boatname']==boat:
            return data

def get_position(boat):
    data=get_boat_data(boat)
    return  (round(data['latitude'],3), round(data['longitude'],3))

def get_race_data(race):
    url=API_RACES[race]
    return requests.get(url).json()['result']

def get_boat_race_data(race, user, boat):
    return get_race_data(race)[user + '-' + boat]
