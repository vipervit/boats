import wx

from boats import ALINGMENT_OFFEST, Thresholds
from boats.lib.gui.box import Box


class NavInfoBox(Box, wx.FlexGridSizer):

    def __init__(self, parent):
        super(Box, self).__init__(5, 2, 0, 100 + ALINGMENT_OFFEST)
        super(NavInfoBox, self).__init__(parent)
        self.boat = parent.boat
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val
        self.update()

    def __draw_layout__(self):
        self.txt_tws_lb = wx.StaticText(self.parent, label='TWS:')
        self.txt_tws_val = wx.StaticText(self.parent)
        self.txt_spd_lb = wx.StaticText(self.parent, label='SPD:')
        self.txt_spd_val = wx.StaticText(self.parent)
        self.txt_heel_lb = wx.StaticText(self.parent, label='HEEL:')
        self.txt_heel_val = wx.StaticText(self.parent)
        self.txt_cog_lb = wx.StaticText(self.parent, label='COG:')
        self.txt_cog_val = wx.StaticText(self.parent)
        self.txt_sails_lb = wx.StaticText(self.parent, label='SAILS:')
        self.txt_sails_val = wx.StaticText(self.parent)
        self.Add(self.txt_tws_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_tws_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_spd_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_spd_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_heel_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_heel_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_cog_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_cog_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_sails_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_sails_val, 0, wx.ALIGN_LEFT)

    def update(self):
        tws = self.data['tws']
        heel = self.data['heel']
        cog = self.data['cog']
        ctd = self.data['ctd']
        spd = self.data['spd']

        self.txt_cog_val.ForegroundColour = 'black'
        self.txt_heel_val.ForegroundColour = 'black'
        self.txt_tws_val.ForegroundColour = 'black'
        self.txt_spd_val.ForegroundColour = 'black'

        if tws > Thresholds.tws:
            self.txt_tws_val.ForegroundColour = 'red'
        if heel > Thresholds.heel:
            self.txt_heel_val.ForegroundColour = 'red'
        if ctd is not None and abs(cog - ctd) > Thresholds.course:
            self.txt_cog_val.ForegroundColour = 'red'
        if spd < Thresholds.spd:
            self.txt_spd_val.ForegroundColour = 'red'
        self.txt_spd_val.SetLabel(str(spd))

        self.txt_tws_val.SetLabel(str(tws))
        self.txt_heel_val.SetLabel(str(heel))
        self.txt_cog_val.SetLabel(str(cog))
        self.txt_sails_val.SetLabel(', '.join(self.data['sails']).upper())
