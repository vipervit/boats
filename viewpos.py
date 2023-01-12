import sys
import time

from selenium import webdriver

from lib.boat import boat

drv = webdriver.Firefox()

sleeptime = int(sys.argv[2])

while True:
    url = 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts-navigation.html#9/LAT/LON'
    oBoat = boat(sys.argv[1])
    oBoat.getdata()
    pos = oBoat.pos
    del oBoat
    url = url.replace('LAT', str(round(pos[0],4)))
    url = url.replace('LON', str(round(pos[1],4)))
    drv.get(url)
    if sleeptime == 0:
        break
    time.sleep(sleeptime)
