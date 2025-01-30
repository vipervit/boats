import wx

from boats import ALINGMENT_OFFEST
from boats.lib.gui.box import Box


class LastDist(Box, wx.FlexGridSizer):
    def __init__(self, parent):
        super(Box, self).__init__(2, 2, 20 + ALINGMENT_OFFEST)
        super(LastDist, self).__init__(parent)
        self._last_dist = None
        self._total_dist = None
        self._total_days = None

    @property
    def total_days(self):
        return self._total_days

    @total_days.setter
    def total_days(self, val):
        self._total_days = str(val)

    @property
    def total_dist(self):
        return self._total_dist

    @total_dist.setter
    def total_dist(self, val):
        self._total_dist = str(val)

    @property
    def last_dist(self):
        return self._last_dist

    @last_dist.setter
    def last_dist(self, val):
        self._last_dist = str(val)

    def __draw_layout__(self):
        self.txt_24_hrs_dist_lb = wx.StaticText(self.parent, label='Last 24 hrs dist.: ')
        self.txt_24_hrs_dist_val = wx.StaticText(self.parent)
        self.txt_24_hrs_spd_lb = wx.StaticText(self.parent, label='Last 24 hrs speed.: ')
        self.txt_24_hrs_spd_val = wx.StaticText(self.parent)
        self.txt_total_days_lb = wx.StaticText(self.parent, label='Days at sea:')
        self.txt_total_days_val = wx.StaticText(self.parent)
        self.txt_total_dist_lb = wx.StaticText(self.parent, label='Distance sailed:')
        self.txt_total_dist_val = wx.StaticText(self.parent)
        self.Add(self.txt_24_hrs_dist_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_24_hrs_dist_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_24_hrs_spd_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_24_hrs_spd_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_total_days_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_total_days_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_total_dist_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_total_dist_val, 0, wx.ALIGN_LEFT)

    def update(self):
        self.txt_24_hrs_dist_val.SetLabel(self.last_dist)
        self.txt_24_hrs_spd_val.SetLabel(str(round(int(self.last_dist) / 24), ))
        self.txt_total_days_val.SetLabel(self.total_days)
        self.txt_total_dist_val.SetLabel(f'{int(self.total_dist):,}')
