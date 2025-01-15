import argparse
import sys
import time
from datetime import datetime, timedelta

import wx
from geopy import distance

from boats.lib.boat import Boat
from boats.lib.common import miles_to_nautical, seconds_to_formatted_output, get_destination_coordinates, \
    get_estimated_position, calc_course, calc_total_voyage_days, calc_total_voyage_distance


class BoatPopup(wx.Frame):
    polling_interval: int

    def __init__(self, boat_name):
        super(BoatPopup, self).__init__(parent=None, title=boat_name.upper())

        self.dr_params = []
        self.inferred = None

        self.boat = Boat(boat_name)
        self.boat.get_data()
        self.counter = 0

        self.polling_interval = 600000  # every 10 min
        self.__reset_counter__()

        self.poll_timer = wx.Timer(self)
        self.__timer_start__()

        self.heartbeat_timer = wx.Timer(self)
        self.heartbeat_timer.Start(1000)

        self.dest_coors = None

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Status info

        self.txt_info = wx.StaticText(self)
        self.vbox.Add(self.txt_info, 0, wx.ALIGN_LEFT)

        # Polling

        self.txt_poll = wx.StaticText(self, label='Polling interval:')
        self.txt_zoom = wx.StaticText(self, label='Zoom level: ')
        self.edctl_zoom = wx.TextCtrl(self, value=str(self.boat.map.zoom))
        self.edctl_poll = wx.TextCtrl(self, value=str(int(self.polling_interval / 1000)))

        self.vbox.Add(self.txt_poll, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.edctl_poll, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.txt_zoom, 0, wx.ALIGN_RIGHT)
        self.vbox.Add(self.edctl_zoom, 0, wx.ALIGN_RIGHT)

        self.edctl_zoom.Bind(wx.EVT_TEXT, self.__set_zoom__)
        self.edctl_poll.Bind(wx.EVT_TEXT, self.__set_polling_interval__)
        self.Bind(wx.EVT_TIMER, self.__update__, self.poll_timer)

        # Destination

        self.txt_enter_dest = wx.StaticText(self, label='Enter destination:')
        self.edctl_destination = wx.TextCtrl(self)
        self.edctl_dr_lon = wx.TextCtrl(self)
        self.txt_dest_coors = wx.StaticText(self)
        self.btn_enter_dest = wx.Button(self, 0, 'OK')

        self.vbox.Add(self.txt_enter_dest, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.edctl_destination, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.btn_enter_dest, 0, wx.ALIGN_LEFT)  # enter destination
        self.vbox.Add(self.txt_dest_coors, 0, wx.ALIGN_LEFT)

        self.btn_enter_dest.Bind(wx.EVT_BUTTON, self.__set_destination__)

        # DR params

        self.txt_enter_dr = wx.StaticText(self, label='Enter DR parameters\nTime period (hrs):')
        self.edctl_dr_period = wx.TextCtrl(self)
        self.txt_enter_last_lat = wx.StaticText(self, label='Last position lat:')
        self.edctl_dr_last_lat = wx.TextCtrl(self)
        self.txt_enter_last_lon = wx.StaticText(self, label='Last position lon:')
        self.edctl_dr_last_lon = wx.TextCtrl(self)
        self.btn_enter_dr = wx.Button(self, 0, 'OK')
        self.txt_inferred_display = wx.StaticText(self, label='Inferred position:')
        self.txt_inferred = wx.StaticText(self)

        self.vbox.Add(self.txt_enter_dr, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.edctl_dr_period, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_enter_last_lat, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.edctl_dr_last_lat, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_enter_last_lon, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.edctl_dr_last_lon, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.btn_enter_dr, 0, wx.ALIGN_LEFT)  # enter DR params
        self.vbox.Add(self.txt_inferred_display, 0, wx.ALIGN_LEFT)
        self.vbox.Add(self.txt_inferred, 0, wx.ALIGN_LEFT)

        self.btn_enter_dr.Bind(wx.EVT_BUTTON, self.__calculate_dr__)

        # Updates info

        self.txt_time = wx.StaticText(self)
        self.txt_last_update = wx.StaticText(self)
        self.txt_next_upd = wx.StaticText(self)

        self.vbox.Add(self.txt_last_update, 0, wx.ALIGN_LEFT)  # last update time
        self.vbox.Add(self.txt_time, 0, wx.ALIGN_LEFT)  # current time
        self.vbox.Add(self.txt_next_upd, 0, wx.ALIGN_LEFT)  # next update time

        # Buttons

        self.btn_open_map = wx.Button(self, 0, 'Open map')
        self.btn_update = wx.Button(self, 0, 'Update Now')
        self.btn_exit = wx.Button(self, 0, 'Exit')

        self.btn_open_map_dr = wx.Button(self, 0, 'Open DR map')

        self.vbox.Add(self.btn_open_map, -2, wx.ALIGN_CENTER)  # Open map
        self.vbox.Add(self.btn_open_map_dr, -2, wx.ALIGN_CENTER)  # Open DR map
        self.vbox.Add(self.btn_update, -2, wx.ALIGN_CENTER)  # Update Now
        self.vbox.Add(self.btn_exit, -1, wx.ALIGN_CENTER)  # Exit

        self.btn_exit.Bind(wx.EVT_BUTTON, self.__close__)
        self.btn_update.Bind(wx.EVT_BUTTON, self.__update__)

        self.btn_open_map.Bind(wx.EVT_BUTTON, self.__open_map_known__)  # open map with actual known position
        self.btn_open_map_dr.Bind(wx.EVT_BUTTON, self.__open_map_dr__)  # open map with inferred (DR) position
        self.Bind(wx.EVT_TIMER, self.__update_display__, self.heartbeat_timer)

        self.SetSizer(self.vbox)

        self.Centre()
        self.Show()

    def __reset_counter__(self):
        self.counter = int(self.polling_interval / 1000)

    def __update_counter__(self):
        self.counter -= 1
        if self.counter == 0:
            self.__reset_counter__()

    def __get_destination__(self):
        return self.edctl_destination.GetLineText(0)

    def __set_destination__(self, event):
        self.dest_coors = get_destination_coordinates(self.__get_destination__())
        self.txt_dest_coors.SetLabel(self.dest_coors.__str__().replace('[', '').replace(']', ''))
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
        self.txt_time.SetLabel(f'Current time:   {curr_time}')
        self.txt_next_upd.SetLabel(f'Next update:    {next_update} (in {seconds_to_formatted_output(self.counter)})')

    def __set_polling_interval__(self, event):
        self.polling_interval = int(event.GetString()) * 1000
        self.__reset_counter__()
        self.__timer_start__()

    def __set_zoom__(self, event):
        self.boat.map.zoom = event.GetString()

    def __timer_start__(self):
        self.poll_timer.Start(self.polling_interval)

    def __open_map_known__(self, event):
        if self.boat.map is None:
            self.boat.get_data()
        self.boat.map.show(self.__get_last_update_timestamp__())

    def __open_map_dr__(self, event):
        self.boat.map.show_calculated_position(self.inferred)

    def __calculate_dr__(self, event):
        self.__get_dead_reckoning_params__()
        self.__infer_position__()

    def __get_dead_reckoning_params__(self):
        lat = self.edctl_dr_last_lat.GetLineText(0)
        lon = self.edctl_dr_last_lon.GetLineText(0)
        period = self.edctl_dr_period.GetLineText(0)
        self.dr_params.append(float(period))
        self.dr_params.append((float(lat), float(lon)))

    def __infer_position__(self):
        period = self.dr_params[0]
        last_pos = self.dr_params[1]
        df = self.boat.get_logged_data()
        delta = timedelta(hours=period)
        cutoff_idx = [x for x in df.index if x >= df.index[-1] - delta][0]
        dfdr = df[df.index >= cutoff_idx]
        mean_spd = dfdr['spd'].mean()
        mean_hdg = dfdr['hdg'].mean()
        self.inferred = get_estimated_position(last_pos, mean_hdg, mean_spd, elapsed=period)
        self.txt_inferred.SetLabel(f'({self.inferred[0]}, {self.inferred[1]})')

    def __update_txt_info__(self):
        df = self.boat.get_logged_data()
        coors_port = self.dest_coors
        hrs_24 = df.index[-1] - timedelta(days=1)
        df_24hrs = df[df.index.isin([entry for entry in df.index if entry >= hrs_24])]
        start_pos = list(df_24hrs.iloc[0][['lat', 'lon']].values)
        last_pos = list(df_24hrs.iloc[-1][['lat', 'lon']].values)
        dist_24hrs = round(miles_to_nautical(distance.distance(start_pos, last_pos).miles))
        avg_spd_24hrs = round(dist_24hrs / 24)
        heel = self.boat.heel
        spd = self.boat.nav['spd']
        hdg = self.boat.nav['hdg']
        cog = self.boat.nav['cog']
        tws = self.boat.wind['tws']
        twd = abs(self.boat.wind['twd'])
        s_sails = ', '.join(self.boat.sailplan).upper()
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
            ctd = calc_course(self.boat.pos, coors_port)  # course to destination
            text += f'CTD: ...............................{ctd}\n'
            text += f'COG: ...............................{cog}\n'
            text += f'HDG: ...............................{hdg}\n\n'
            text += f'DTD: ...............................{dtw:,} nm\n'
            text += f'TTD: ...............................{timedelta(hours=time2go)} h\n'
            text += f'ETA: ...............................{txteta}\n'

        self.txt_info.SetLabel(text)

    def __update__(self, event):
        self.boat.get_data()
        self.__update_txt_info__()

    @staticmethod
    def __close__(event):
        sys.exit()


def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    args = parser.parse_args(args)

    app = wx.App()
    BoatPopup(boat_name=args.boat_name)
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
