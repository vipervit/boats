import sys
import time
import webbrowser

from lib.boat import boat
from lib.common import URL_IBOATING_CHART


boatname = sys.argv[1]
sleeptime = int(sys.argv[2])
zoom = str(sys.argv[3])

while True:
    url = '{}#ZOOM/LAT/LON'.format(URL_IBOATING_CHART)
    oBoat = boat(boatname)
    oBoat.getdata()
    pos = oBoat.pos
    del oBoat
    url = url.replace('LAT', str(round(pos[0],4)))
    url = url.replace('LON', str(round(pos[1],4)))
    url = url.replace('ZOOM', zoom)
    webbrowser.open(url)
    if sleeptime == 0:
        break
    time.sleep(sleeptime)
