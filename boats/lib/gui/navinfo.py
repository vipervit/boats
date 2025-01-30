import wx

from boats import ALINGMENT_OFFEST
from boats.lib.gui.box import Box


class NavInfoBox(Box, wx.FlexGridSizer):

    def __init__(self, parent):
        super(Box, self).__init__(4, 2, 0, 100 + ALINGMENT_OFFEST)
        super(NavInfoBox, self).__init__(parent)
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
        self.txt_sails_lb = wx.StaticText(self.parent, label='SAILS:')
        self.txt_sails_val = wx.StaticText(self.parent)
        self.Add(self.txt_tws_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_tws_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_spd_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_spd_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_heel_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_heel_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_sails_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_sails_val, 0, wx.ALIGN_LEFT)

    def update(self):
        self.txt_tws_val.SetLabel(str(self.data['tws']))
        self.txt_spd_val.SetLabel(str(self.data['spd']))
        self.txt_heel_val.SetLabel(str(self.data['heel']))
        self.txt_sails_val.SetLabel(', '.join(self.data['sails']).upper())
