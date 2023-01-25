#!/usr/bin/env python
# coding: utf-8
from boats.lib.common import get_all_own_boats_json
from boats.lib.boat import Boat


response=get_all_own_boats_json()
boats = [Boat(each['boatname']) for each in response]

for boat in boats:
    boat.getdata(response)
    print('')
    boat.show()
