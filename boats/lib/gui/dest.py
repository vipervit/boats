from datetime import timedelta, datetime

import wx
from geopy.distance import distance

from boats.lib.common import get_destination_coordinates, calc_course, miles_to_nautical
from boats.lib.gui.box import Box


class DestinationBox(Box, wx.FlexGridSizer):
    def __init__(self, parent):
        self.box_calc = wx.FlexGridSizer(3, 2, 0, 120)
        super(Box, self).__init__(2, 5, 0, 0)
        super(DestinationBox, self).__init__(parent)
        self.dest_coors = None
        self.name = None
        self._ttd = None
        self._dtd = None
        self._ctd = None
        self._eta = None
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @property
    def ctd(self):
        return self._ctd

    def __set_destination__(self, event):
        self.edbox_dest_coors.ForegroundColour = 'green'
        self.__get_destination__()
        self.dest_coors = get_destination_coordinates(self.name)
        self.parent.boat.nav.wpt = self.dest_coors
        if self.dest_coors is not False:
            self.edbox_dest_coors.SetLabel(self.name)
            self.update()
        else:
            self.edbox_dest_coors.ForegroundColour = 'red'
            self.edbox_dest_coors.SetLabel('NOT FOUND!')
            self.txt_ctd_val.SetLabel('')
            self.txt_eta_val.SetLabel('')
        self.parent.__update_navinfo__()

    def __get_destination__(self):
        if len(self.edbox_destination.GetLineText(0)) > 0:
            self.name = self.edbox_destination.GetLineText(0)

    def update(self):
        if self.name is not None and len(self.name) > 0:
            self.__calculate_destination_info__()
            self.edbox_destination.SetLabel(self.name)
            self.edbox_dest_coors.SetLabel(self.dest_coors.__str__().replace('[', '').replace(']', ''))
            self.txt_ctd_val.SetLabel(str(self._ctd))
            self.txt_dtd_val.SetLabel(str(f'{self._dtd:,}'))
            # TODO Red colour if ETA exceeds threshold
            self.txt_eta_val.SetLabel(self._eta)

    def __calculate_destination_info__(self):
        spd = self.data['spd']
        pos = self.data['pos']
        if self.dest_coors is not None:
            self._dtd = round(miles_to_nautical(distance(self.dest_coors, pos).miles))
            if spd == 0:
                self._ttd = 0
                self._eta = 'N/A'
            else:
                self._ttd = round(self._dtd / spd)
                self._eta = (datetime.now() + timedelta(hours=self._ttd)).strftime('%d-%b %H:%M')
            self._ctd = calc_course(pos, self.dest_coors)  # course to destination

    def __draw_layout__(self):
        txt_enter_dest = wx.StaticText(self.parent, label='Destination:')
        self.edbox_destination = wx.TextCtrl(self.parent)
        self.edbox_dest_coors = wx.TextCtrl(self.parent)
        self.edbox_dest_coors.Disable()
        btn_enter_dest = wx.Button(self.parent, 0, 'Enter')
        self.txt_ctd_lb = wx.StaticText(self.parent, label='CTD:')
        self.txt_ctd_val = wx.StaticText(self.parent)
        self.txt_dtd_lb = wx.StaticText(self.parent, label='DTD:')
        self.txt_dtd_val = wx.StaticText(self.parent)
        self.txt_eta_lb = wx.StaticText(self.parent, label='ETA:')
        self.txt_eta_val = wx.StaticText(self.parent)
        self.Add(txt_enter_dest, wx.ALIGN_LEFT)
        self.AddSpacer(2)
        self.Add(self.edbox_destination, 0, wx.ALIGN_LEFT)
        self.Add(self.edbox_dest_coors, 0, wx.ALIGN_LEFT)
        self.Add(btn_enter_dest, 0, wx.ALIGN_LEFT)  # Enter button
        self.box_calc.AddMany([self.txt_ctd_lb,
                               self.txt_ctd_val,
                               self.txt_dtd_lb,
                               self.txt_dtd_val,
                               self.txt_eta_lb,
                               self.txt_eta_val,
                               ])
        self.Add(self.box_calc)
        btn_enter_dest.Bind(wx.EVT_BUTTON, self.__set_destination__)
