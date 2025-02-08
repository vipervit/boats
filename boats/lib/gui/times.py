import time
from datetime import datetime

import wx

from boats import ALINGMENT_OFFEST, DATETIME_FORMAT
from boats.lib.common import seconds_to_formatted_output
from boats.lib.gui.box import Box


class Times(Box, wx.FlexGridSizer):

    def __init__(self, parent):
        super(Box, self).__init__(3, 2, 0, 60 + ALINGMENT_OFFEST)
        super(Times, self).__init__(parent)
        self._last_update = None
        self._counter = None

    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, val):
        self._last_update = val
        self.update()

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, val):
        self._counter = val

    def __draw_layout__(self):
        self.txt_curr_time_lb = wx.StaticText(self.parent, label='Current time:')
        self.txt_curr_time_val = wx.StaticText(self.parent)
        self.txt_last_update_lb = wx.StaticText(self.parent, label='Last update:')
        self.txt_last_update_val = wx.StaticText(self.parent)
        self.txt_next_update_lb = wx.StaticText(self.parent, label='Next update:')
        self.txt_next_update_val = wx.StaticText(self.parent)
        self.Add(self.txt_curr_time_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_curr_time_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_last_update_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_last_update_val, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_next_update_lb, 0, wx.ALIGN_LEFT)
        self.Add(self.txt_next_update_val, 0, wx.ALIGN_LEFT)

    def update(self):
        curr_time = time.time()
        curr_time_s = datetime.fromtimestamp(curr_time).strftime(DATETIME_FORMAT)
        last_update_ts = self.parent.boat.log.last_record_timestamp
        next_update = last_update_ts + self.parent.timer.period
        next_update_ts = datetime.fromtimestamp(next_update).strftime(DATETIME_FORMAT)
        next_in_secs = (datetime.fromtimestamp(next_update) - datetime.fromtimestamp(curr_time)).seconds
        self.txt_curr_time_val.SetLabel(curr_time_s)
        self.txt_last_update_val.SetLabel(self.last_update)
        self.txt_next_update_val.SetLabel(f'{next_update_ts} (in {seconds_to_formatted_output(next_in_secs)})')
