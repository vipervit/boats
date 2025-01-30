import sys

import wx

from boats.lib.gui.box import Box


class ButtonsBox(Box, wx.FlexGridSizer):
    def __init__(self, parent):
        super(Box, self).__init__(2, 0, 5)
        super(ButtonsBox, self).__init__(parent)
        btn_update = wx.Button(self.parent, label='Update')
        btn_close = wx.Button(self.parent, label='Close')
        self.Add(btn_update)
        self.Add(btn_close)
        btn_update.Bind(wx.EVT_BUTTON, self.parent.__update_all__)  # Update
        btn_close.Bind(wx.EVT_BUTTON, sys.exit)  # Close
