import argparse
import sys
import time
from datetime import datetime, timedelta

import wx
import wx.html2
from geopy import distance

from boats.lib.boat import Boat
from boats.lib.common import miles_to_nautical, seconds_to_formatted_output, get_destination_coordinates, \
    calc_course, calc_total_voyage_days, calc_total_voyage_distance


class Display(wx.Frame):

    def __init__(self, boat_name):
        super(Display, self).__init__(parent=None, title=boat_name.upper())

        self.polling_interval = 600000  # every 10 min
        self.zoom = 10
        self.poll_counter = 0
        self.dest_coors = None
        self.txt_info = None
        self.destination = None

        self.boat = Boat(boat_name, getdata=False)
        self.__update_nav_data__()

        self.polling_timer = wx.Timer(self)
        self.polling_timer.Start(self.polling_interval)
        self.__reset_polling_counter__()

        self.edctl_zoom = None

        self.heartbeat_timer = wx.Timer(self)
        self.heartbeat_timer.Start(1000)

        self.Bind(wx.EVT_TIMER, self.__heartbeat_update__, self.heartbeat_timer)
        self.Bind(wx.EVT_TIMER, self.__update_all__, self.polling_timer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.__redraw_layout__()
        self.SetSizer(self.sizer)

        self.Centre()
        self.Show()

    def __redraw_layout__(self):
        self.sizer.Clear(delete_windows=True)
        self.sizer.Add(self.__map__(), 1, wx.EXPAND)
        self.sizer.Add(self.__polling__())
        self.sizer.Add(self.__times__())
        self.sizer.Add(self.__destination__())
        self.sizer.Add(self.__main_info__())
        self.sizer.Add(self.__buttons__(), 0, 5)
        self.sizer.Layout()

    def __buttons__(self):
        box = wx.FlexGridSizer(3, 0, 5)
        btn_update = wx.Button(self, label='Update')
        btn_close = wx.Button(self, label='Close')
        box.Add(btn_update)  # Update
        box.Add(btn_close)  # Close
        btn_update.Bind(wx.EVT_BUTTON, self.__update_all__)  # Update
        btn_close.Bind(wx.EVT_BUTTON, self.__close__)  # Close
        return box

    def __map__(self):
        # TODO Map does not show the correct timestamp when app is launched - shows the previous log entry
        mapbox = wx.BoxSizer(wx.VERTICAL)
        browser = wx.html2.WebView.New(self)
        browser.LoadURL(f'file:///{self.boat.map.mfile}')
        mapbox.Add(browser, 1, wx.EXPAND)
        return mapbox

    def __polling__(self):
        box = wx.FlexGridSizer(0, 0, 0)
        txt_poll = wx.StaticText(self, label='Polling interval:')
        txt_zoom = wx.StaticText(self, label='Zoom level: ')
        btn_enter = wx.Button(self, label='Enter')
        self.edctl_zoom = wx.TextCtrl(self, value=str(self.zoom))
        self.edctl_poll = wx.TextCtrl(self, value=str(int(self.polling_interval / 1000)))
        box.Add(txt_poll, 0, wx.ALIGN_RIGHT)
        box.Add(self.edctl_poll, 0, wx.ALIGN_RIGHT)
        box.Add(txt_zoom, 0, wx.ALIGN_RIGHT)
        box.Add(self.edctl_zoom, 0, wx.ALIGN_RIGHT)
        box.Add(btn_enter, 0, wx.ALIGN_RIGHT)
        btn_enter.Bind(wx.EVT_BUTTON, self.__set_zoom_and_polling_interval)
        return box

    def __set_zoom_and_polling_interval(self, event):
        self.__set_zoom__()
        self.__set_polling_interval__()
        self.__redraw_layout__()
        self.__set_destination__(None)

    def __set_polling_interval__(self):
        self.polling_interval = int(self.edctl_poll.GetLineText(0)) * 1000
        self.__reset_polling_counter__()

    def __set_zoom__(self):
        val = self.edctl_zoom.GetLineText(0)
        if val is not None:
            self.zoom = int(val)
        self.boat.map.set(zoom_start=self.zoom)

    def __destination__(self):
        box = wx.BoxSizer(wx.HORIZONTAL)
        txt_enter_dest = wx.StaticText(self, label='Destination:')
        self.edbox_destination = wx.TextCtrl(self)
        self.txt_dest_coors = wx.StaticText(self)
        btn_enter_dest = wx.Button(self, 0, 'Enter')
        box.Add(txt_enter_dest, 0, wx.ALIGN_LEFT)
        box.Add(self.edbox_destination, 0, wx.ALIGN_LEFT)
        box.Add(self.txt_dest_coors, 0, wx.ALIGN_LEFT)
        box.Add(btn_enter_dest, 0, wx.ALIGN_LEFT)  # enter destination
        btn_enter_dest.Bind(wx.EVT_BUTTON, self.__set_destination__)
        return box

    def __main_info__(self):
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_info = wx.StaticText(self)
        box.Add(self.txt_info)
        self.__update_nav_info_display__()
        return box

    def __times__(self):
        box = wx.BoxSizer(wx.VERTICAL)
        self.txt_curr_time = wx.StaticText(self)
        self.txt_last_update = wx.StaticText(self)
        self.txt_next_upd = wx.StaticText(self)
        box.Add(self.txt_last_update, 0, wx.ALIGN_LEFT)  # last update time
        box.Add(self.txt_curr_time, 0, wx.ALIGN_LEFT)  # current time
        box.Add(self.txt_next_upd, 0, wx.ALIGN_LEFT)  # next update time
        return box

    def __heartbeat_update__(self, event):
        self.__update_polling_counter__(event)
        self.__update_times_display__()

    def __update_times_display__(self):
        curr_time = time.strftime('%d-%b %H:%M')
        next_update = (datetime.now() + timedelta(seconds=self.poll_counter)).strftime('%d-%b %H:%M')
        last_update = self.__get_last_update_timestamp__()
        self.txt_last_update.SetLabel(f'Last update:    {last_update}')
        self.txt_curr_time.SetLabel(f'Current time:   {curr_time}')
        self.txt_next_upd.SetLabel(
            f'Next update:    {next_update} (in {seconds_to_formatted_output(self.poll_counter)})')

    def __update_polling_counter__(self, event):
        self.poll_counter -= 1
        if self.poll_counter == 0:
            self.__reset_polling_counter__()

    def __reset_polling_counter__(self):
        self.poll_counter = int(self.polling_interval / 1000)

    def __update_all__(self, event):
        self.__update_nav_data__()
        self.__reset_polling_counter__()
        self.__redraw_layout__()
        self.__set_zoom__()
        self.__set_destination__(None)

    def __update_nav_data__(self):
        self.boat.update_from_server(savetolog=True)

    def __update_nav_info_display__(self):
        df = self.boat.log.df
        coors_port = self.dest_coors
        hrs_24 = df.index[-1] - timedelta(days=1)
        df_24hrs = df[df.index.isin([entry for entry in df.index if entry >= hrs_24])]
        start_pos = list(df_24hrs.iloc[0][['lat', 'lon']].values)
        last_pos = list(df_24hrs.iloc[-1][['lat', 'lon']].values)
        dist_24hrs = round(miles_to_nautical(distance.distance(start_pos, last_pos).miles))
        avg_spd_24hrs = round(dist_24hrs / 24)
        heel = self.boat.nav.heel
        spd = self.boat.nav.speed['spd']
        hdg = self.boat.nav.az['hdg']
        tws = self.boat.nav.wind['tws']
        twd = abs(self.boat.nav.wind['twd'])
        s_sails = ', '.join(self.boat.nav.sailplan).upper()
        total_days = calc_total_voyage_days(df.index[0], df.index[-1])
        total_distance = calc_total_voyage_distance(df[['lat', 'lon']])
        text = f'Last 24 hrs dist.: ...........{dist_24hrs}\n'
        text += f'Last 24 hrs avg spd: ......{avg_spd_24hrs}\n'
        text += f'TWS: ...............................{tws}\n'
        text += f'SPD: ...............................{spd}\n'
        text += f'HEEL: ..............................{heel}\n'
        text += f'TWD: ...............................{twd}\n\n'
        text += f'{s_sails}\n\n'
        text += f'Days at sea: {total_days}\n'
        text += f'Distance sailed: {total_distance:,} nm\n\n'
        if coors_port is not None:
            dtw = round(miles_to_nautical(distance.distance(coors_port, last_pos).miles))
            time2go = round(dtw / spd)
            txteta = (datetime.now() + timedelta(hours=time2go)).strftime('%d-%b %H:%M')
            ctd = calc_course(self.boat.nav.position, coors_port)  # course to destination
            text += f'CTD: ...............................{ctd}\n'
            # TODO: COG only exists in data from the server but the monitor displays data from log. Solve!
            if 'cog' in self.boat.nav.az.keys():
                cog = self.boat.nav.az['cog']
                text += f'COG: ...............................{cog}\n'
            text += f'HDG: ...............................{hdg}\n\n'
            text += f'DTD: ...............................{dtw:,} nm\n'
            text += f'TTD: ...............................{timedelta(hours=time2go)} h\n'
            text += f'ETA: ...............................{txteta}\n'
        self.txt_info.SetLabel(text)

    def __set_destination__(self, event):
        self.__get_destination__()
        if self.destination is not None and len(self.destination) > 0:
            self.dest_coors = get_destination_coordinates(self.destination)
            self.edbox_destination.SetLabel(self.destination)
            self.txt_dest_coors.SetLabel(self.dest_coors.__str__().replace('[', '').replace(']', ''))
            self.__update_nav_info_display__()

    def __get_destination__(self):
        if len(self.edbox_destination.GetLineText(0)) > 0:
            self.destination = self.edbox_destination.GetLineText(0)

    def __get_last_update_timestamp__(self):
        self.boat.log.load()
        return self.boat.log.last_record_timestamp_local

    def __open_map___(self, event):
        if self.boat.map is None:
            self.boat.map.show(self.__get_last_update_timestamp__())

    @staticmethod
    def __close__(event):
        sys.exit()


def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    args = parser.parse_args(args)

    app = wx.App()
    Display(args.boat_name)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
