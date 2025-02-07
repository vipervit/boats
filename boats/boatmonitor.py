import argparse
import sys

import wx
import wx.html2

from boats.lib.boat import Boat
from boats.lib.common import get_version_from_pyproject
from boats.lib.gui.buttons import ButtonsBox
from boats.lib.gui.dest import DestinationBox
from boats.lib.gui.lastdist import LastDist
from boats.lib.gui.mapbox import MapBox
from boats.lib.gui.navinfo import NavInfoBox
from boats.lib.gui.times import Times
from boats.lib.gui.zoompoll import ZoomPollBox
from boats.lib.utimer import UTimer


class Display(wx.Frame):

    #

    def __init__(self, boat_name, version):
        super(Display, self).__init__(parent=None, title=f'{boat_name.upper()}  v{version}')
        self.boat = Boat(boat_name, getdata=True, savetolog=True)
        self.initial_update = True
        self.timer = UTimer(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.box_map = MapBox(self.boat.map.mfile, self)
        self.box_navinfo = NavInfoBox(self)
        self.box_last_dist = LastDist(self)
        self.box_poll_zoom = ZoomPollBox(self)
        self.box_times = Times(self)
        self.box_buttons = ButtonsBox(self)
        self.box_dest = DestinationBox(self)

        self.sizer.Add(self.box_map, 1, wx.EXPAND)
        self.sizer.Add(self.box_poll_zoom)
        self.sizer.Add(self.box_times)
        self.sizer.Add(self.box_last_dist)
        self.sizer.Add(self.box_navinfo, wx.ALIGN_LEFT)
        self.sizer.Add(self.box_dest, wx.ALIGN_LEFT)
        self.sizer.Add(self.box_buttons, 0, 5)

        self.__update_all__(event=None)

        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()

        self.SetInitialSize((500, 500))
        self.SetMinSize((0, 0))
        self.Centre()
        self.Show()

    def __heartbeat__(self):
        self.box_times.counter = self.timer.counter
        self.box_times.update()

    def __update_all__(self, event):
        self.__update_nav_data__()
        self.box_times.update()
        self.box_map.update()
        self.box_dest.update()
        self.__update_totals__()
        self.__update_navinfo__()

    def __update_totals__(self):
        self.box_last_dist.last_dist = self.boat.log.last_24_hrs_distance
        self.box_last_dist.total_days = self.boat.log.total_days
        self.box_last_dist.total_dist = self.boat.log.total_distance
        self.box_last_dist.update()

    def __update_navinfo__(self):
        data = {}
        data.update({'tws': self.boat.nav.wind['tws']})
        data.update({'spd': self.boat.nav.speed['spd']})
        data.update({'heel': self.boat.nav.heel})
        data.update({'cog': self.boat.nav.az['cog']})
        data.update({'ctd': self.box_dest.ctd})
        data.update({'sails': self.boat.nav.sailplan})
        self.box_navinfo.data = data

    def __update_nav_data__(self):
        if __debug__:
            assert self.boat.savetolog == True
            if self.initial_update is False:
                self.boat.update_from_server()
        self.initial_update = False
        self.box_times.last_update = self.boat.log.last_record_timestamp_local
        self.box_dest.data = {'spd': int(self.boat.nav.speed['spd']), 'pos': self.boat.nav.position}


def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    args = parser.parse_args(args)

    app = wx.App()
    Display(boat_name=args.boat_name, version=get_version_from_pyproject())
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
