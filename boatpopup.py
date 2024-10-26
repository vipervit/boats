import argparse
import sys
import time
from datetime import datetime, timedelta

import wx
from geopy import distance

from boats.lib.boat import Boat
from boats.lib.common import miles_to_nautical, seconds_to_formatted_output, get_destination_coordinates


class BoatPopup(wx.Frame):
    polling_interval: int

    def __init__(self, boat_name):
        super(BoatPopup, self).__init__(parent=None, title=boat_name.upper())

        self.boat = Boat(boat_name)
        self.counter = 0

        self.polling_interval = 600000  # every 10 min
        self.__reset_counter__()

        self.poll_timer = wx.Timer(self)
        self.__timer_start__()

        self.heartbeat_timer = wx.Timer(self)
        self.heartbeat_timer.Start(1000)

        self.dest_coors = None

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.txt_info = wx.StaticText(self)
        self.txt_poll = wx.StaticText(self, label='Polling interval:')
        self.txt_zoom = wx.StaticText(self, label='Zoom level: ')
        self.edctl_zoom = wx.TextCtrl(self, value=str(self.boat.map.zoom))
        self.edctl_poll = wx.TextCtrl(self, value=str(int(self.polling_interval/1000)))
        self.txt_enter_dest = wx.StaticText(self, label='Enter destination:')
        self.edctl_destination = wx.TextCtrl(self)
        self.txt_dest_coors = wx.StaticText(self)
        self.txt_next_upd = wx.StaticText(self)
        self.txt_time = wx.StaticText(self)
        self.txt_last_update = wx.StaticText(self)
        self.btn_open_map = wx.Button(self, 0, 'Open map')
        self.btn_update = wx.Button(self, 0, 'Update Now')
        self.btn_exit = wx.Button(self, 0, 'Exit')
        self.btn_enter_dest = wx.Button(self, 0, 'OK')

        self.vbox.Add(self.txt_info, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_enter_dest, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.edctl_destination, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.btn_enter_dest, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_dest_coors, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_poll, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.edctl_poll, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.txt_zoom, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.edctl_zoom, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.txt_time, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_last_update, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_next_upd, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.btn_open_map, -2, wx.ALIGN_CENTER) # Open map
        self.vbox.Add(self.btn_update, -2, wx.ALIGN_CENTER) # Update Now
        self.vbox.Add(self.btn_exit, -1, wx.ALIGN_CENTER) # Exit

        self.Bind(wx.EVT_TIMER, self.__update__, self.poll_timer)
        self.edctl_zoom.Bind(wx.EVT_TEXT, self.__set_zoom__)
        self.edctl_poll.Bind(wx.EVT_TEXT, self.__set_polling_interval__)
        self.btn_exit.Bind(wx.EVT_BUTTON, self.__close__)
        self.btn_update.Bind(wx.EVT_BUTTON, self.__update__)
        self.btn_open_map.Bind(wx.EVT_BUTTON, self.__open_map__)
        self.Bind(wx.EVT_TIMER, self.__update_display__, self.heartbeat_timer)
        self.btn_enter_dest.Bind(wx.EVT_BUTTON, self.__set_destination__)

        self.SetSizer(self.vbox)

        self.Centre()
        self.Show()

    def __reset_counter__(self):
        self.counter = int(self.polling_interval/1000)

    def __update_counter__(self):
        self.counter -= 1
        if self.counter == 0:
            self.__reset_counter__()

    def __get_destination__(self):
        return self.edctl_destination.GetLineText(0)

    def __set_destination__(self, event):
        self.dest_coors =  get_destination_coordinates(self.__get_destination__())
        self.txt_dest_coors.SetLabel(self.dest_coors.__str__())
        self.__update_txt_info__()

    def __get_last_update_timestamp__(self):
        return datetime.fromtimestamp(self.boat.get_logged_data().iloc[-1].name.timestamp()).strftime('%d-%b %H:%M')

    def __update_display__(self, event):
        self.__update_txt_info__()
        self.__update_counter__()
        curr_time = time.strftime('%d-%b %H:%M')
        next_update = (datetime.now() + timedelta(seconds=self.counter)).strftime('%d-%b %H:%M')
        last_update = self.__get_last_update_timestamp__()
        self.txt_last_update.SetLabel(f'Last update:    {last_update}')
        self.txt_next_upd.SetLabel(f'Next update:    {next_update} (in {seconds_to_formatted_output(self.counter)})')
        self.txt_time.SetLabel(f'Current time:   {curr_time}')

    def __set_polling_interval__(self, event):
        self.polling_interval = int(event.GetString())*1000
        self.__reset_counter__()
        self.__timer_start__()

    def __set_zoom__(self, event):
        self.boat.map.zoom = event.GetString()

    def __timer_start__(self):
        self.poll_timer.Start(self.polling_interval)

    @staticmethod
    def __close__(event):
        sys.exit()

    def __open_map__(self, event):
        if self.boat.map is None:
            self.boat.get_data()
        self.boat.map.show(self.__get_last_update_timestamp__())

    def __update_txt_info__(self):
        df = self.boat.get_logged_data()
        coors_port=self.dest_coors
        hrs_24 = df.index[-1] - timedelta(days=1)
        df_24hrs = df[df.index.isin([entry for entry in df.index if entry >= hrs_24])]
        start_pos = list(df_24hrs.iloc[0][['lat', 'lon']].values)
        last_pos = list(df_24hrs.iloc[-1][['lat', 'lon']].values)
        dist_24hrs = round(miles_to_nautical(distance.distance(start_pos, last_pos).miles))
        avg_spd_24hrs = round(dist_24hrs / 24)
        spd = df.iloc[-1]['spd']
        text =  f'Last 24 hrs dist.:...........{dist_24hrs}\n'
        text += f'Last 24 hrs avg spd:......{avg_spd_24hrs}\n'
        text += f'Last speed:....................{spd}\n'
        if coors_port is not None:
            dtw = round(miles_to_nautical(distance.distance(coors_port, last_pos).miles))
            time2go = round(dtw / spd)
            text += f'DTD:...............................{dtw:,} nm\n'
            text += f'TTD:...............................{timedelta(hours=time2go)} h\n'
            text += f'ETA:...............................{(datetime.now() + timedelta(hours=time2go)).strftime('%d-%b %H:%M')}'
        self.txt_info.SetLabel(text)

    def __update__(self, event):
        self.boat.get_data()
        self.__update_txt_info__()

def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    args = parser.parse_args(args)

    app = wx.App()
    BoatPopup(boat_name=args.boat_name)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
