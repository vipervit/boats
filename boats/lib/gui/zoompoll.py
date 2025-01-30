import wx

from boats.lib.gui.box import Box


class ZoomPollBox(Box, wx.FlexGridSizer):

    def __init__(self, parent):
        self.poll_choice_hrs = ['00', '01', '02', '03', '04']
        self.poll_choice_mins = ['00', '10', '20', '40']
        super(Box, self).__init__(3, 2, 0, 20)
        super(ZoomPollBox, self).__init__(parent)
        self._polling_interval = 600000  # every 10 min
        self._polling_counter = None
        self.zoom = 10

        self.polling_timer = wx.Timer()
        self.__reset_poliing_timer__()

    @property
    def polling_interval(self):
        return self._polling_interval

    @polling_interval.setter
    def polling_interval(self, val):
        self._polling_interval = val

    @property
    def polling_counter(self):
        return self._polling_counter

    @polling_counter.setter
    def polling_counter(self, val):
        self._polling_counter = val

    def __draw_layout__(self):
        self.Add(self.__polling__())
        self.Add(self.__zooming__(), wx.EXPAND)

    def __polling__(self):
        box = wx.BoxSizer(wx.HORIZONTAL)
        txt_poll = wx.StaticText(self.parent, label='Polling interval (hrs:min):')
        btn_enter = wx.Button(self.parent, label='Enter')
        self.combo_poll_hrs = wx.ComboBox(self.parent, choices=self.poll_choice_hrs, style=wx.CB_READONLY)
        self.combo_poll_mins = wx.ComboBox(self.parent, choices=self.poll_choice_mins, style=wx.CB_READONLY)
        self.combo_poll_mins.SetValue('10')
        box.Add(txt_poll, 0, wx.ALIGN_LEFT)
        box.Add(self.combo_poll_hrs)
        box.Add(self.combo_poll_mins)
        box.Add(btn_enter, 0, wx.ALIGN_LEFT)
        btn_enter.Bind(wx.EVT_BUTTON, self.__set_polling_interval__)
        return box

    def __zooming__(self):
        zoom_choice = [str(i) for i in range(20)]
        box = wx.BoxSizer(wx.HORIZONTAL)
        txt_zoom = wx.StaticText(self.parent, label='Zoom level:')
        self.combo_zoom = wx.ComboBox(self.parent, choices=zoom_choice, style=wx.CB_READONLY)
        box.Add(txt_zoom, 0, wx.EXPAND)
        box.Add(self.combo_zoom)
        self.combo_zoom.Bind(wx.EVT_COMBOBOX, self.__set_zoom__)
        return box

    def __set_zoom__(self, event):
        self.zoom = self.combo_zoom.GetSelection()
        self.parent.boat.map.set(zoom_start=self.zoom)
        self.parent.box_map.update()

    def __set_polling_interval__(self, event):
        hrs = self.combo_poll_hrs.GetValue()
        mins = self.combo_poll_mins.GetValue()
        if (hrs == self.poll_choice_hrs[0]) and (mins == self.poll_choice_mins[0]):
            self.combo_poll_mins.SetValue(self.poll_choice_mins[1])
            mins = self.combo_poll_mins.GetValue()
        self.polling_interval = 1000 * (int(hrs) * 3600 + int(mins) * 60)
        self.__reset_polling_counter__()

    def heartbeat(self, timestamp):
        self.polling_counter -= 1
        if self.polling_counter == 0:
            self.__reset_polling_counter__()

    def __reset_polling_counter__(self):
        self.polling_counter = self.polling_interval / 1000

    def __reset_poliing_timer__(self):
        self.__reset_polling_counter__()
        self.polling_timer.Start(self.polling_interval)
