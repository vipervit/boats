import sys

from lib.boat import boat

if sys.argv[1] == '--full':
    full = True
else:
    full = False
    
boat = boat('Petsamo')
boat.getdata()
boat.show(full)
boat.save_current_sail_data()