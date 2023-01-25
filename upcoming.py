#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import datetime
import pytz

from bs4 import BeautifulSoup


def get_races(o_races):
    return o_races.find_all('a')


def get_mileage(o_race):
    return round(float(o_race.find_all_next('td')[3].contents[0].strip(' NM')))


def get_race_name(o_race):
    return o_race.contents[0]


def get_race_time(o_race):
    return datetime.datetime.fromisoformat(o_race.find_all_next('span')[1].contents[0]).astimezone(
        pytz.timezone('EST')).strftime('%A %d-%h %I:%M %p')


short_mileage = 50

r = requests.get('https://sarl.ingenium.net.au/index')

soup = BeautifulSoup(r.text, 'html.parser')
upcoming = soup.find('table')

data = [(get_race_name(race), get_mileage(race), get_race_time(race)) for race in get_races(upcoming)]

df = pd.DataFrame(data, columns=['Race', 'Mileage', 'Time'])
df_short_on_weekends = df[
    (df['Mileage'] < short_mileage) & (df['Time'].str.contains('Saturday') | df['Time'].str.contains('Sunday'))]

print(df)
print('------------------\nShort starting on weekends:\n {}'.format(df_short_on_weekends))
