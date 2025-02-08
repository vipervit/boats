import wx

from boats.lib.gui.box import Box


class MapBox(Box, wx.BoxSizer):

    def __init__(self, mapfile, parent):
        self._map = None
        self._f = mapfile
        super(Box, self).__init__()
        super(MapBox, self).__init__(parent)

    def __create_map__(self):
        browser = wx.html2.WebView.New(self.parent)
        browser.LoadURL(f'file:///{self._f}')
        self._map = browser

    def __draw_layout__(self):
        self.__create_map__()
        self.Add(self._map, 1, wx.EXPAND)

    def update(self):
        self.Detach(self._map)
        self.__draw_layout__()
        self.Layout()
