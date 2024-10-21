import argparse
import sys
from datetime import datetime, timedelta

import wx
from geopy import distance

from boats.lib.boat import Boat
from boats.lib.common import miles_to_nautical


class BoatPopup(wx.Frame):

    def __init__(self, boat_name):
        super(BoatPopup, self).__init__(parent=None, title=boat_name.upper())

        self.boat = Boat(boat_name)
        self.boat.map._loc = []

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.txt_info = wx.StaticText(self)
        self.txt_timestamp = wx.StaticText(self)
        self.btn_exit = wx.Button(self, 0, 'Exit')
        self.btn_open_map = wx.Button(self, 0, 'Open map')
        self.btn_update = wx.Button(self, 0, 'Update')

        self.vbox.Add(self.txt_info, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.btn_open_map, -2, wx.ALIGN_CENTER)
        self.vbox.Add(self.btn_update, -2, wx.ALIGN_CENTER)
        self.vbox.Add(self.btn_exit, -1, wx.ALIGN_CENTER)
        self.vbox.Add(self.txt_timestamp, 0, wx.ALIGN_LEFT)

        self.btn_exit.Bind(wx.EVT_BUTTON, self.__close__)
        self.btn_update.Bind(wx.EVT_BUTTON, self.__get_update_from_webserver__)
        self.btn_open_map.Bind(wx.EVT_BUTTON, self.__open_map__)

        self.__get_update_from_log__()

        self.SetSizer(self.vbox)

        self.Centre()
        self.Show()

    @staticmethod
    def __close__(event):
        sys.exit()

    def __get_last_update_timestamp__(self):
        return datetime.fromtimestamp(self.boat.get_logged_data().iloc[-1].name.timestamp()).strftime('%d-%b %H:%M')

    def __open_map__(self, event):
        if self.boat.map is not None:
            self.boat.map.show(self.__get_last_update_timestamp__())
        else:
            self.__update_txt_info__('Get boat data update first!')

    def __update_txt_timestamp__(self):
        self.txt_timestamp.SetLabel(f'Last update {self.__get_last_update_timestamp__()}')

    def __update_txt_info__(self, text):
        self.txt_info.SetLabel(text)

    def __get_update_from_webserver__(self, event):
        self.boat.get_data()
        self.__get_update_from_log__()

    def __get_update_from_log__(self):
        df = self.boat.get_logged_data()
        self.boat.map._loc = list(self.boat.get_logged_data().iloc[-1][['lat', 'lon']].values)
        hrs_24 = df.index[-1] - timedelta(days=1)
        df_24hrs = df[df.index.isin([entry for entry in df.index if entry >= hrs_24])]
        start_pos = list(df_24hrs.iloc[0][['lat', 'lon']].values)
        last_pos = list(df_24hrs.iloc[-1][['lat', 'lon']].values)
        dist_24hrs = round(miles_to_nautical(distance.distance(start_pos, last_pos).miles))
        avg_spd_24hrs = round(dist_24hrs / 24)
        # dtw = round(miles_to_nautical(distance.distance(coors_port, last_pos).miles))
        # spd = df.iloc[-1]['spd']
        # time2go = round(dtw / spd)
        self.__update_txt_info__(f'Last 24 hours: \n--------------\ndistance: {dist_24hrs}\navg speed: {avg_spd_24hrs}')
        self.__update_txt_timestamp__()

def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    args = parser.parse_args(args)

    app = wx.App()
    BoatPopup(boat_name=args.boat_name)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
