import wx

from boats.lib.gui.box import Box


class MapBox(Box, wx.BoxSizer):

    def __init__(self, mapfile, parent):
        super(Box, self).__init__()
        super(MapBox, self).__init__(parent)
        self._map = None
        self.f = mapfile
        self.__add_map__()

    def __create_map__(self):
        browser = wx.html2.WebView.New(self.parent)
        browser.LoadURL(f'file:///{self.f}')
        self._map = browser

    def __add_map__(self):
        self.__create_map__()
        self.Add(self._map, 1, wx.EXPAND)

    def update(self):
        self.Detach(self._map)
        self.__add_map__()
        self.Layout()
