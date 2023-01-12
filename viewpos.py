import sys
import time

from selenium import webdriver

from lib.boat import boat

drv = webdriver.Firefox()

sleeptime = int(sys.argv[2])
zoom = str(sys.argv[3])

while True:
    url = 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts-navigation.html#ZOOM/LAT/LON'
    oBoat = boat(sys.argv[1])
    oBoat.getdata()
    pos = oBoat.pos
    del oBoat
    url = url.replace('LAT', str(round(pos[0],4)))
    url = url.replace('LON', str(round(pos[1],4)))
    url = url.replace('ZOOM', zoom)
    drv.get(url)
    if sleeptime == 0:
        break
    time.sleep(sleeptime)
