#! /opt/anaconda3/bin/python3

from boats.lib.boat import Boat

with Boat('Petsamo') as boat:
    print(boat.get_logged_data())
