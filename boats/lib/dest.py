import os

import pandas as pd

from boats import DIR_TEST_FILES, F_DESTINATIONS

F_TEST_DESTINATIONS = os.path.join(DIR_TEST_FILES, 'test_dest.csv')

if not __debug__:
    F_DEST = F_TEST_DESTINATIONS
else:
    F_DEST = F_DESTINATIONS


class Destinations:

    def __init__(self):
        self._df = None
        self.__read_from_file__()

    @property
    def df(self):
        return self._df

    def view(self):
        print(self._df)

    def add_new(self, place, coors):
        if place not in list(self._df['Name']):
            newrow = pd.DataFrame({'Name': [place], 'Lat': coors[0], 'Lon': coors[1]})
            self._df = pd.concat([self._df, newrow])
            self.__write_to_file()
            self.__read_from_file__()
            print(self.df.tail(1))
        else:
            print('Already exists!')
            print(self._df[self._df['Name'] == place])
            return -1

    def remove(self, name):
        self.__read_from_file__()
        idx = self._df[self._df['Name'] == name].index
        self._df.drop(idx, inplace=True)
        self.__write_to_file()

    def __read_from_file__(self):
        self._df = pd.read_csv(F_DEST)

    def __write_to_file(self):
        self._df.to_csv(F_DEST, index=False)
