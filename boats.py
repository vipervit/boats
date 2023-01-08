#!/usr/bin/env python
# coding: utf-8
from lib.common import get_all_own_boats_json
from lib.boat import boat


response=get_all_own_boats_json()
boats=[boat(each['boatname']) for each in response]

for boat in boats:
    boat.getdata(response)
    print('')
    boat.show()
