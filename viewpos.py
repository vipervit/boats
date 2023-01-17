import sys
import webbrowser

from lib.boat import boat
from lib.common import URL_IBOATING_CHART, timestamp

boat_name = sys.argv[1]
zoom = str(sys.argv[2])
full = True

url = '{}#ZOOM/LAT/LON'.format(URL_IBOATING_CHART)
oBoat = boat(boat_name)
oBoat.getdata()
oBoat.save_current_sail_data()
pos = oBoat.pos
url = url.replace('LAT', str(round(pos[0], 4)))
url = url.replace('LON', str(round(pos[1], 4)))
url = url.replace('ZOOM', zoom)
webbrowser.open(url)
oBoat.show(full)
print('\nAs of: {}'.format(timestamp()))