import wx


class DashboardTheme:
    FRAME_BG = "#07141c"
    MAP_BG = "#061018"
    PANEL_BG = "#0f2533"
    PANEL_INSET = "#18384a"
    PANEL_BORDER = "#2e576d"
    TEXT = "#e8f1f6"
    TEXT_MUTED = "#9db4c2"
    ACCENT = "#3db7d6"
    SUCCESS = "#72d39a"
    WARNING = "#ff8f6b"
    BUTTON_BG = "#dce7ee"
    BUTTON_BG_ALT = "#d7edf4"
    INPUT_BG = "#f4f7f9"
    INPUT_TEXT = "#102635"
    RAIL_WIDTH = 420


def make_font(size, weight=wx.FONTWEIGHT_NORMAL, family=wx.FONTFAMILY_SWISS):
    return wx.Font(size, family, wx.FONTSTYLE_NORMAL, weight)


def style_panel(widget, bg=None, fg=None):
    if bg is not None:
        widget.SetBackgroundColour(bg)
    if fg is not None and hasattr(widget, "SetForegroundColour"):
        widget.SetForegroundColour(fg)


def style_button(button, accent=False):
    button.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
    button.SetFont(make_font(10, wx.FONTWEIGHT_BOLD))
    button.SetMinSize((-1, 34))
    button.SetForegroundColour(DashboardTheme.INPUT_TEXT)
    if accent:
        button.SetBackgroundColour(DashboardTheme.BUTTON_BG_ALT)
    else:
        button.SetBackgroundColour(DashboardTheme.BUTTON_BG)


def style_input(widget):
    widget.SetFont(make_font(10))
    widget.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
    widget.SetMinSize((-1, 34))
    widget.SetForegroundColour(DashboardTheme.INPUT_TEXT)
    widget.SetBackgroundColour(DashboardTheme.INPUT_BG)


def style_label(widget, muted=False, size=9, bold=False):
    widget.SetForegroundColour(DashboardTheme.TEXT_MUTED if muted else DashboardTheme.TEXT)
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    widget.SetFont(make_font(size, weight))
