import wx

from boats import DEFAULT_UPDATE_INTERVAL


class UTimer(wx.Timer):

    def __init__(self, owner):
        wx.Timer.__init__(self, owner)
        self.owner = owner
        self._counter = None
        self._period = DEFAULT_UPDATE_INTERVAL
        self.__reset_counter__()
        super().Start(1000)

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, val):
        self._period = int(val)
        self.__reset_counter__()

    @property
    def counter(self):
        return self._counter

    def Notify(self):
        self.owner.__heartbeat__()
        self._counter -= 1
        if self._counter <= 0:
            self.Action()
            self.__reset_counter__()

    def Action(self):
        self.owner.__update_all__(None)

    def __reset_counter__(self):
        self._counter = self.period
