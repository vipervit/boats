#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import datetime
import pytz
from pytz import timezone

from bs4 import BeautifulSoup

from boats.lib.common import URL_RACES_SCHEDULE


def get_races(o_races):
    return o_races.find_all('a')


def get_mileage(o_race):
    return round(float(o_race.find_all_next('td')[3].contents[0].strip(' NM')))


def get_race_name(o_race):
    return o_race.contents[0]


def get_race_time(o_race):
    return pytz.utc.localize(datetime.datetime.fromisoformat(o_race.find_all_next('span')[1].contents[0].strip('Z')),
                             is_dst=None).astimezone(timezone('America/Toronto')).strftime('%A %d-%h %I:%M %p')


def main():
    short_mileage = 5

    r = requests.get(URL_RACES_SCHEDULE)

    soup = BeautifulSoup(r.text, 'html.parser')
    upcoming = soup.find('table')

    data = [(get_race_name(race), get_mileage(race), get_race_time(race)) for race in get_races(upcoming)]

    df = pd.DataFrame(data, columns=['Race', 'Mileage', 'Time'])
    df_short_on_weekends = df[
        (df['Mileage'] < short_mileage) & (df['Time'].str.contains('Saturday') | df['Time'].str.contains('Sunday'))]

    print(df)
    print('------------------\nShort (< {} nm) starting on weekends:\n {}'.format(short_mileage, df_short_on_weekends))


if __name__ == '__main__':
    main()
