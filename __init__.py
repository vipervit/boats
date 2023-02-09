import os
from pathlib import Path

DIR_HOME = Path(__file__).parent.resolve()
DIR_DATA = os.path.join(DIR_HOME, 'data')
DIR_SAILDATA = os.path.join(DIR_DATA, 'perf')
DIR_RACEMARKS = os.path.join(DIR_DATA, 'races')
DIR_ROUTE = os.path.join(DIR_HOME, 'route')
DIR_ROUTE_IN = os.path.join(DIR_ROUTE, 'in')
DIR_ROUTE_OUT = os.path.join(DIR_ROUTE, 'out')
DIR_ROUTE_TMP = os.path.join(DIR_ROUTE, 'tmp')
DIR_HTML = os.path.join(DIR_HOME, 'map')
DIR_PKL = os.path.join(DIR_DATA, 'pkl')