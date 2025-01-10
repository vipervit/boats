import os
import json
import time
import warnings
from io import StringIO

import pandas as pd

from boats import DIR_LOGS, DIR_TEST_FILES
from boats.lib.common import make_log_file_name


class Log:

    def __init__(self, boat_name):
        warnings.simplefilter(action='ignore', category=FutureWarning)
        location = DIR_LOGS
        if not __debug__: # the logic is inverted; to run  in debug mode '-O' must be used
            location = DIR_TEST_FILES
        self._file = os.path.join(location, make_log_file_name(boat_name))
        self._track = None
        self._df = None
        if self.__exists__():
            self.load()

    @property
    def track(self):
        return self._track

    @staticmethod
    def required_columns():
        return ['hdg',
                'tws',
                'spd',
                'twd',
                'twa',
                'heel',
                'lat',
                'lon',
                'sails']

    def load(self):
        if self.__exists__():
            self.__make_df__()
            self.__get_track__()
        else:
            raise FileNotFoundError(f'Log file not found: {self._file}.')

    def add_new(self, newrec):
        data = {}
        assert list(newrec.keys()) == self.required_columns()
        if self.__exists__():
            data = self.__read_from_file__()
        data.update({str(time.time()): newrec})
        self.__write_to_file__(data)

    @property
    def df(self):
        return self._df

    @property
    def last_record(self):
        return self._df.iloc[-1]

    @property
    def last_record_timestamp(self):
        return self.last_record.name.strftime('%d-%b %H:%M')

    def __exists__(self):
        res = os.path.exists(self._file)
        if not res:
            warnings.warn(f'Log file not found: {self._file}.')
        return res

    def __get_track__(self):
        if self._df is not None:
            df = self._df.copy()
            df.sort_index(ascending=False, inplace=True)
            df_track = df[['lat', 'lon']].dropna()
            self._track = [[df_track.loc[i, 'lat'], df_track.loc[i, 'lon']] for i in df_track.index]
        else:
            raise ValueError('self._df is None.')

    def __make_df__(self):
        self._df = pd.read_json(StringIO(json.dumps(self.__read_from_file__())), orient='index')

    def __read_from_file__(self):
        try:
            with open(self._file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f'Log file does not exist: \'{self._file}\'.')

    def __write_to_file__(self, dic):
        with open(self._file, 'w') as f:
            json.dump(dic, f)
