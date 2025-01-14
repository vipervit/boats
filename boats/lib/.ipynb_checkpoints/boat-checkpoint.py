import json
import time

import pandas as pd

from boats.lib import common
from boats.lib.common import get_all_own_boats_json


class boat:
    
    def __init__(self, name):
        self.name=name
        self.datafile= common.os.path.join(common.DIR_SAILDATA, name + '_dat.json')
     
    def getdata(self, response_json=False):
        if not response_json:
            response_json = get_all_own_boats_json()
        for data in response_json:
            if data['boatname'] == self.name:
                self.data = data
        self.sails=[sail['sail'] for sail in self.data['sails']]
        self.sailplan=[sail['sail'] for sail in self.data['sails'] if sail['halyard']==1 and sail['furled']==0]
        self.pos=(round(self.data['latitude'],5), round(self.data['longitude'],5))
        self.heel=round(self.data['heeldegrees'],)
        self.wind={'tws': round(self.data['tws']*2,1),
                   'twa': round(self.data['twa']),
                   'twd': round(self.data['twd']),
                   'aws': round(self.data['aws']*2),
                   'awa': round(self.data['awa'])}
        self.nav={'hdg': round(self.data['hdg']),
                  'spd': round(self.data['spd']*2,1),
                  'cog': round(self.data['cog']),
                  'sog': round(self.data['sog']*2,1),
                  'whlm': round(self.data['weatherhelm'],2)
                 }
        
    def show_pos(self):
        print('lat: {}'.format(self.pos[0]))
        print('lon: {}'.format(self.pos[1]))
    
    def show_sailplan(self):
        for sail in self.sails:
            mark=''
            if sail in self.sailplan:
                mark='X'
            print(sail.lower() + ':' + ' '*(16-len(sail)) + mark)
            
    def show_heel(self):
        print('heel: {}'.format(self.heel))
            
    def show_speed(self):
        print('tws: {}'.format(self.wind['tws']))
        print('spd: {}'.format(self.nav['spd']))
        print('sog: {}'.format(self.nav['sog']))
              
    def show_course(self):
        print('hdg: {}'.format(self.nav['hdg']))
        print('cog: {}'.format(self.nav['cog']))
        
    def __show_short__(self):
        self.show_pos()
        print('hdg: {}'.format(self.nav['hdg']))
        print('cog: {}'.format(self.nav['cog']))    
        print('tws: {}'.format(self.wind['tws']))

    def __show_full__(self):
        self.show_pos()
        print('\n')        
        self.show_sailplan()
        print('\n')
        for each in self.nav:
            print('{}: {}'.format(each, self.nav[each]))
        for each in self.wind:
            print('{}: {}'.format(each, self.wind[each]))
        self.show_heel()
        
    def show(self, full=False):
        print('{}\n----------------'.format(self.name.upper()))
        if full:
            self.__show_full__()
        else:
            self.__show_short__()
            
    def sail_config_snapshot(self):
        return {'tws': self.wind['tws'],
                'spd': self.nav['spd'],
                'twd': self.wind['twd'],
                'twa': self.wind['twa'],
                'heel': self.heel,
                'sails': self.sailplan}
    
    def __read_sail_data_from_file__(self):
        with open(self.datafile, 'r') as f:
            return json.load(f)
    
    def __write_sail_data_to_file__(self, dic):
            with open(self.datafile, 'w') as f:
                json.dump(dic, f)       
    
    def save_current_sail_data(self):
        data={}
        if common.os.path.exists(self.datafile):
            data=self.__read_sail_data_from_file__()
        data.update({str(time.time()): self.sail_config_snapshot()})
        self.__write_sail_data_to_file__(data)
    
    def get_sail_data(self):
        return pd.read_json(json.dumps(self.__read_sail_data_from_file__()), orient='index')
        