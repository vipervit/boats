import os
from pathlib import Path

import keyring

DIR_HOME = Path(__file__).parent.resolve()
DIR_DATA = os.path.join(DIR_HOME, 'data')
DIR_MAPS = os.path.join(DIR_HOME, 'map')
DIR_SAILDATA = os.path.join(DIR_DATA, 'perf')
DIR_RACEMARKS = os.path.join(DIR_DATA, 'races')
DIR_ROUTE = os.path.join(DIR_HOME, 'route')
DIR_ROUTE_IN = os.path.join(DIR_ROUTE, 'in')
DIR_ROUTE_OUT = os.path.join(DIR_ROUTE, 'out')
DIR_ROUTE_TMP = os.path.join(DIR_ROUTE, 'tmp')
DIR_PKL = os.path.join(DIR_DATA, 'pkl')

SAILS = [
    'Nr.1',
    'Nr.2',
    'Nr.3',
    'Stormjib',
    'Mainsail',
    'Genaker',
    'Mizzen',
    'Mizzen staysail'
]

POINTS_OF_SAIL = {
    'close haul': list(range(0, 37)),
    'close reach': list(range(36, 73)),
    'beam': list(range(72, 109)),
    'broad reach': list(range(108, 145)),
    'run': list(range(144, 181))
}


API_KEY = keyring.get_password('sailaway', 'api_key')
API_USER = keyring.get_password('sailaway', 'api_user')

API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr={}&key={}'.format(API_USER, API_KEY)

DEFAULT_ZOOM = 7

F_DESTINATIONS = os.path.join(DIR_DATA, 'destinations.csv')
