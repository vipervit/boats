from datetime import datetime, timedelta
from pathlib import Path
import wx
import wx.html2
from geopy.distance import distance

from boats import DATETIME_FORMAT, DEFAULT_ZOOM, Thresholds
from boats.lib.common import calc_course, curr_time, miles_to_nautical, seconds_to_formatted_output
from boats.lib.dest import Destinations
from boats.lib.gui.theme import DashboardTheme, make_font, style_button, style_input, style_label, style_panel


def rail_wrap_width():
    return DashboardTheme.RAIL_WIDTH - 92


class SectionCard(wx.Panel):
    def __init__(self, parent, title, collapsed=False):
        super().__init__(parent)
        self.title = title
        self.expanded = not collapsed

        style_panel(self, DashboardTheme.PANEL_BG, DashboardTheme.TEXT)

        outer = wx.BoxSizer(wx.VERTICAL)
        self.header = wx.Button(self, style=wx.BORDER_NONE | wx.BU_LEFT)
        self.header.SetForegroundColour(DashboardTheme.TEXT)
        self.header.SetBackgroundColour(DashboardTheme.PANEL_BG)
        self.header.SetFont(make_font(12, wx.FONTWEIGHT_BOLD))
        self.header.Bind(wx.EVT_BUTTON, self.on_toggle)

        self.body = wx.Panel(self)
        style_panel(self.body, DashboardTheme.PANEL_INSET, DashboardTheme.TEXT)
        self.body_sizer = wx.BoxSizer(wx.VERTICAL)
        self.body.SetSizer(self.body_sizer)

        outer.Add(self.header, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)
        outer.Add(self.body, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(outer)
        self.SetMinSize((DashboardTheme.RAIL_WIDTH - 24, -1))

        self._sync_header()
        self.set_collapsed(collapsed)

    def _sync_header(self):
        marker = "v" if self.expanded else ">"
        self.header.SetLabel(f"{marker} {self.title.upper()}")

    def on_toggle(self, event):
        self.set_collapsed(self.expanded)

    def set_collapsed(self, collapsed):
        self.expanded = not collapsed
        self.body.Show(self.expanded)
        self._sync_header()
        self.Layout()
        parent = self.GetParent()
        if parent is not None:
            parent.Layout()
            if hasattr(parent, "FitInside"):
                parent.FitInside()


def add_metric_row(parent, sizer, label, emphasized=False):
    row = wx.BoxSizer(wx.VERTICAL)
    title = wx.StaticText(parent, label=label.upper())
    value = wx.StaticText(parent, label="--")
    style_label(title, muted=True, size=9, bold=True)
    style_label(value, size=14 if emphasized else 12, bold=emphasized)
    value.Wrap(rail_wrap_width())
    row.Add(title, 0, wx.BOTTOM, 3)
    row.Add(value, 0)
    sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 10)
    return value


class MapBox(wx.Panel):
    def __init__(self, parent, mapfile, on_map_event=None):
        super().__init__(parent)
        self._mapfile = mapfile
        self._on_map_event = on_map_event
        style_panel(self, DashboardTheme.MAP_BG, DashboardTheme.TEXT)

        self.browser = wx.html2.WebView.New(self)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.on_title_changed)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)
        self.load_map()

    def set_mapfile(self, mapfile):
        self._mapfile = mapfile

    def load_map(self):
        self.browser.LoadURL(f"{Path(self._mapfile).resolve().as_uri()}?ts={curr_time()}")

    def update(self):
        self.load_map()

    def set_pick_mode(self, enabled):
        self.browser.RunScript(f"window.boatsTargetPickEnabled = {str(bool(enabled)).lower()};")

    def on_title_changed(self, event):
        title = event.GetString()
        if self._on_map_event is None:
            event.Skip()
            return

        if title.startswith("map-click:"):
            raw_coords = title.split(":", 1)[1]
            parts = raw_coords.split(",")
            lat = float(parts[0])
            lon = float(parts[1])
            zoom = int(parts[2]) if len(parts) > 2 else None
            center = None
            if len(parts) > 4:
                center = (float(parts[3]), float(parts[4]))
            self._on_map_event("pick", (lat, lon, zoom, center))
        elif title == "map-target-clear":
            self._on_map_event("clear", None)
        elif title.startswith("map-pick-cancel"):
            zoom, center = None, None
            if ":" in title:
                parts = title.split(":", 1)[1].split(",")
                zoom = int(parts[0])
                if len(parts) > 2:
                    center = (float(parts[1]), float(parts[2]))
            self._on_map_event("cancel-pick", (zoom, center))
        elif title.startswith("map-view-state:"):
            parts = title.split(":", 1)[1].split(",")
            zoom = int(parts[0])
            center = (float(parts[1]), float(parts[2]))
            self._on_map_event("view-state", (zoom, center))
        event.Skip()


class StatusPanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Status", collapsed=False)
        self.current_value = add_metric_row(self.body, self.body_sizer, "Current")
        self.last_value = add_metric_row(self.body, self.body_sizer, "Last update")
        self.next_value = add_metric_row(self.body, self.body_sizer, "Next update")
        self.state_value = add_metric_row(self.body, self.body_sizer, "State", emphasized=True)

    def set_state(self, text, tone="neutral"):
        tones = {
            "neutral": DashboardTheme.TEXT,
            "active": DashboardTheme.ACCENT,
            "success": DashboardTheme.SUCCESS,
            "warning": DashboardTheme.WARNING,
        }
        self.state_value.SetForegroundColour(tones.get(tone, DashboardTheme.TEXT))
        self.state_value.SetLabel(text)
        self.state_value.Wrap(rail_wrap_width())

    def update(self, ts_last_update, ts_next_update):
        now = curr_time()
        self.current_value.SetLabel(datetime.fromtimestamp(now).strftime(DATETIME_FORMAT))
        if ts_last_update is None:
            self.last_value.SetLabel("--")
        else:
            self.last_value.SetLabel(datetime.fromtimestamp(ts_last_update).strftime(DATETIME_FORMAT))
        if ts_next_update is None:
            self.next_value.SetLabel("--")
        else:
            countdown = max(0, int(ts_next_update - now))
            next_update = datetime.fromtimestamp(ts_next_update).strftime(DATETIME_FORMAT)
            self.next_value.SetLabel(f"{next_update} ({seconds_to_formatted_output(countdown)})")
        self.next_value.Wrap(rail_wrap_width())


class HelmPanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Helm", collapsed=False)
        self.tws_value = add_metric_row(self.body, self.body_sizer, "True wind", emphasized=True)
        self.spd_value = add_metric_row(self.body, self.body_sizer, "Boat speed", emphasized=True)
        self.heel_value = add_metric_row(self.body, self.body_sizer, "Heel")
        self.cog_value = add_metric_row(self.body, self.body_sizer, "Course over ground")
        self.sails_value = add_metric_row(self.body, self.body_sizer, "Sails")
        self.sails_value.Wrap(rail_wrap_width())

    def update(self, data):
        tws = data["tws"]
        spd = data["spd"]
        heel = data["heel"]
        cog = data["cog"]
        ctd = data["ctd"]

        for widget in (self.tws_value, self.spd_value, self.heel_value, self.cog_value):
            widget.SetForegroundColour(DashboardTheme.TEXT)

        if tws > Thresholds.tws:
            self.tws_value.SetForegroundColour(DashboardTheme.WARNING)
        if spd < Thresholds.spd:
            self.spd_value.SetForegroundColour(DashboardTheme.WARNING)
        if heel > Thresholds.heel:
            self.heel_value.SetForegroundColour(DashboardTheme.WARNING)

        cog_label = f"{cog} deg"
        if ctd is not None and cog != ctd:
            diff = abs(cog - ctd)
            cog_label = f"{cog} deg / off {diff} deg"
            self.cog_value.SetForegroundColour(DashboardTheme.WARNING)

        self.tws_value.SetLabel(f"{tws} kt")
        self.spd_value.SetLabel(f"{spd} kt")
        self.heel_value.SetLabel(f"{heel} deg")
        self.cog_value.SetLabel(cog_label)
        self.sails_value.SetLabel(", ".join(data["sails"]).upper())
        self.sails_value.Wrap(rail_wrap_width())


class PassagePanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Passage", collapsed=True)
        self.last_dist_value = add_metric_row(self.body, self.body_sizer, "24h distance")
        self.last_speed_value = add_metric_row(self.body, self.body_sizer, "24h average")
        self.total_days_value = add_metric_row(self.body, self.body_sizer, "Days at sea")
        self.total_dist_value = add_metric_row(self.body, self.body_sizer, "Distance sailed")

    def update(self, last_dist, total_days, total_dist):
        self.last_dist_value.SetLabel(f"{last_dist} nm")
        self.last_speed_value.SetLabel(f"{round(int(last_dist) / 24)} kt")
        self.total_days_value.SetLabel(str(total_days))
        self.total_dist_value.SetLabel(f"{int(total_dist):,} nm")


class DestinationPanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Destination", collapsed=False)
        self.name = None
        self.dest_coors = None
        self._ctd = None
        self.saved_destinations = Destinations().names()

        saved_prompt = wx.StaticText(self.body, label="Saved waypoint")
        style_label(saved_prompt, muted=True, size=9, bold=True)
        self.body_sizer.Add(saved_prompt, 0, wx.BOTTOM, 6)

        self.saved_destination_combo = wx.ComboBox(
            self.body,
            choices=["Select saved destination..."] + self.saved_destinations,
            style=wx.CB_READONLY,
        )
        style_input(self.saved_destination_combo)
        self.saved_destination_combo.SetSelection(0)
        self.saved_destination_combo.Bind(wx.EVT_COMBOBOX, self.on_saved_destination_selected)
        self.body_sizer.Add(self.saved_destination_combo, 0, wx.EXPAND | wx.BOTTOM, 10)

        prompt = wx.StaticText(self.body, label="Manual or selected waypoint")
        style_label(prompt, muted=True, size=9, bold=True)
        self.body_sizer.Add(prompt, 0, wx.BOTTOM, 6)

        entry_row = wx.BoxSizer(wx.HORIZONTAL)
        self.destination_input = wx.TextCtrl(self.body, style=wx.TE_PROCESS_ENTER)
        style_input(self.destination_input)
        self.destination_input.Bind(wx.EVT_TEXT_ENTER, self.on_submit)
        self.submit_button = wx.Button(self.body, label="Set")
        style_button(self.submit_button, accent=True)
        self.submit_button.Bind(wx.EVT_BUTTON, self.on_submit)
        entry_row.Add(self.destination_input, 1, wx.RIGHT, 8)
        entry_row.Add(self.submit_button, 0)
        self.body_sizer.Add(entry_row, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.message = wx.StaticText(self.body, label="Set a waypoint to draw course and ETA.")
        style_label(self.message, muted=True, size=10)
        self.message.Wrap(rail_wrap_width())
        self.body_sizer.Add(self.message, 0, wx.BOTTOM, 10)

        self.coords_value = add_metric_row(self.body, self.body_sizer, "Coordinates")
        self.ctd_value = add_metric_row(self.body, self.body_sizer, "Course to destination", emphasized=True)
        self.dtd_value = add_metric_row(self.body, self.body_sizer, "Distance to destination")
        self.eta_value = add_metric_row(self.body, self.body_sizer, "Eta")

    @property
    def ctd(self):
        return self._ctd

    def on_submit(self, event):
        self.GetTopLevelParent().apply_destination(self.destination_input.GetValue().strip())

    def reload_saved_destinations(self, selected_name=None):
        self.saved_destinations = Destinations().names()
        self.saved_destination_combo.Clear()
        self.saved_destination_combo.Append("Select saved destination...")
        for destination in self.saved_destinations:
            self.saved_destination_combo.Append(destination)
        if selected_name in self.saved_destinations:
            self.saved_destination_combo.SetValue(selected_name)
        else:
            self.saved_destination_combo.SetSelection(0)

    def refresh_message(self):
        self.message.Wrap(rail_wrap_width())
        self.body.Layout()
        self.Layout()
        parent = self.GetParent()
        if parent is not None and hasattr(parent, "FitInside"):
            parent.FitInside()

    def on_saved_destination_selected(self, event):
        value = self.saved_destination_combo.GetValue()
        if value and value != "Select saved destination...":
            self.destination_input.SetValue(value)
            self.message.SetForegroundColour(DashboardTheme.TEXT_MUTED)
            self.message.SetLabel("Saved waypoint selected. Press Set to apply it.")
            self.refresh_message()

    def show_lookup_error(self, name):
        self.message.SetForegroundColour(DashboardTheme.WARNING)
        if name == "blank":
            self.message.SetLabel("Enter a destination name before setting a waypoint.")
        elif self.name is None:
            self.message.SetLabel(f"Destination '{name}' not found.")
        else:
            self.message.SetLabel(f"Destination '{name}' not found. Current waypoint kept.")
        self.refresh_message()

    def activate_destination(self, name, coordinates):
        self.name = name
        self.dest_coors = coordinates
        self.destination_input.SetValue(name)
        if name in self.saved_destinations:
            self.saved_destination_combo.SetValue(name)
        self.message.SetForegroundColour(DashboardTheme.SUCCESS)
        self.message.SetLabel("Waypoint active. Course line is live on the map.")
        self.refresh_message()

    def update_navigation(self, speed, pos):
        if self.dest_coors is None:
            self._ctd = None
            self.coords_value.SetLabel("--")
            self.ctd_value.SetLabel("--")
            self.dtd_value.SetLabel("--")
            self.eta_value.SetLabel("--")
            return

        self.coords_value.SetLabel(f"{self.dest_coors[0]:.4f}, {self.dest_coors[1]:.4f}")
        dtd = round(miles_to_nautical(distance(self.dest_coors, pos).miles))
        self._ctd = calc_course(pos, self.dest_coors)
        if speed == 0:
            eta = "N/A"
        else:
            eta = (datetime.now() + timedelta(hours=(dtd / speed))).strftime("%d-%b %H:%M")
        self.ctd_value.SetLabel(f"{self._ctd} deg")
        self.dtd_value.SetLabel(f"{dtd:,} nm")
        self.eta_value.SetLabel(eta)


class ControlsPanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Controls", collapsed=True)
        self.poll_choice_hrs = ["00", "01", "02", "03", "04"]
        self.poll_choice_mins = ["00", "10", "20", "40"]
        self.zoom_choice = [str(i) for i in range(20)]

        poll_label = wx.StaticText(self.body, label="Polling interval")
        style_label(poll_label, muted=True, size=9, bold=True)
        self.body_sizer.Add(poll_label, 0, wx.BOTTOM, 6)

        poll_row = wx.BoxSizer(wx.HORIZONTAL)
        self.combo_poll_hrs = wx.ComboBox(self.body, choices=self.poll_choice_hrs, style=wx.CB_READONLY)
        self.combo_poll_mins = wx.ComboBox(self.body, choices=self.poll_choice_mins, style=wx.CB_READONLY)
        style_input(self.combo_poll_hrs)
        style_input(self.combo_poll_mins)
        self.combo_poll_hrs.SetMinSize((84, 34))
        self.combo_poll_mins.SetMinSize((84, 34))
        self.apply_poll_button = wx.Button(self.body, label="Apply")
        style_button(self.apply_poll_button)
        self.apply_poll_button.Bind(wx.EVT_BUTTON, self.on_set_polling_interval)
        poll_row.Add(self.combo_poll_hrs, 0, wx.RIGHT, 8)
        poll_row.Add(self.combo_poll_mins, 0, wx.RIGHT, 8)
        poll_row.Add(self.apply_poll_button, 0)
        self.body_sizer.Add(poll_row, 0, wx.BOTTOM, 12)

        zoom_label = wx.StaticText(self.body, label="Map zoom")
        style_label(zoom_label, muted=True, size=9, bold=True)
        self.body_sizer.Add(zoom_label, 0, wx.BOTTOM, 6)

        self.combo_zoom = wx.ComboBox(self.body, choices=self.zoom_choice, style=wx.CB_READONLY)
        style_input(self.combo_zoom)
        self.combo_zoom.SetMinSize((110, 34))
        self.combo_zoom.Bind(wx.EVT_COMBOBOX, self.on_set_zoom)
        self.body_sizer.Add(self.combo_zoom, 0, wx.BOTTOM, 14)

        action_row = wx.BoxSizer(wx.HORIZONTAL)
        self.refresh_button = wx.Button(self.body, label="Refresh")
        style_button(self.refresh_button, accent=True)
        self.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh)
        action_row.Add(self.refresh_button, 0, wx.RIGHT, 8)

        self.close_button = wx.Button(self.body, label="Close")
        style_button(self.close_button)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close)
        action_row.Add(self.close_button, 0)
        self.body_sizer.Add(action_row, 0)

        self.set_poll_period(600)
        self.set_zoom(DEFAULT_ZOOM)

    @property
    def zoom(self):
        value = self.combo_zoom.GetStringSelection() or self.combo_zoom.GetValue()
        return int(value) if value else DEFAULT_ZOOM

    @staticmethod
    def _set_combo_selection(combo, value):
        if not combo.SetStringSelection(str(value)):
            combo.SetValue(str(value))

    def set_poll_period(self, seconds):
        hrs = min(int(seconds // 3600), int(self.poll_choice_hrs[-1]))
        mins = int((seconds % 3600) / 60)
        minute_choice = str(mins).zfill(2)
        if minute_choice not in self.poll_choice_mins:
            minute_choice = self.poll_choice_mins[1]
        self._set_combo_selection(self.combo_poll_hrs, str(hrs).zfill(2))
        self._set_combo_selection(self.combo_poll_mins, minute_choice)

    def set_zoom(self, zoom):
        self._set_combo_selection(self.combo_zoom, str(zoom))

    def on_set_zoom(self, event):
        self.GetTopLevelParent().set_zoom(self.zoom)

    def on_set_polling_interval(self, event):
        hrs = self.combo_poll_hrs.GetStringSelection() or self.combo_poll_hrs.GetValue() or self.poll_choice_hrs[0]
        mins = self.combo_poll_mins.GetStringSelection() or self.combo_poll_mins.GetValue() or self.poll_choice_mins[1]
        if hrs == "00" and mins == "00":
            mins = self.poll_choice_mins[1]
            self._set_combo_selection(self.combo_poll_mins, mins)
        self.GetTopLevelParent().set_polling_interval(int(hrs), int(mins))

    def on_refresh(self, event):
        self.GetTopLevelParent().__update_all__(event)

    def on_close(self, event):
        self.GetTopLevelParent().Close()


class RailHeader(wx.Panel):
    def __init__(self, parent, boat_name, version):
        super().__init__(parent)
        style_panel(self, DashboardTheme.FRAME_BG, DashboardTheme.TEXT)
        title = wx.StaticText(self, label=boat_name.upper())
        title.SetFont(make_font(18, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(DashboardTheme.TEXT)

        subtitle = wx.StaticText(self, label=f"Marine monitor v{version}")
        style_label(subtitle, muted=True, size=10)

        note = wx.StaticText(self, label="Map-first view with cleaner native controls.")
        style_label(note, muted=True, size=10)
        note.Wrap(DashboardTheme.RAIL_WIDTH - 48)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.BOTTOM, 2)
        sizer.Add(subtitle, 0, wx.BOTTOM, 4)
        sizer.Add(note, 0)
        self.SetSizer(sizer)


class MapPickPanel(SectionCard):
    def __init__(self, parent):
        super().__init__(parent, "Map Pick", collapsed=False)
        self.pick_mode_enabled = False
        self.has_selection = False

        self.message = wx.StaticText(self.body, label="Enable course mode to place a point on the map.")
        style_label(self.message, muted=True, size=10)
        self.message.Wrap(rail_wrap_width())
        self.body_sizer.Add(self.message, 0, wx.BOTTOM, 10)

        self.coords_value = add_metric_row(self.body, self.body_sizer, "Selected point")
        self.course_value = add_metric_row(self.body, self.body_sizer, "Course to point", emphasized=True)
        self.distance_value = add_metric_row(self.body, self.body_sizer, "Distance to point")

        action_row_top = wx.BoxSizer(wx.HORIZONTAL)
        self.mode_button = wx.Button(self.body, label="Pick course point")
        style_button(self.mode_button, accent=True)
        self.mode_button.Bind(wx.EVT_BUTTON, self.on_toggle_mode)
        action_row_top.Add(self.mode_button, 0, wx.RIGHT, 8)

        self.copy_button = wx.Button(self.body, label="Copy coords")
        style_button(self.copy_button)
        self.copy_button.Bind(wx.EVT_BUTTON, self.on_copy)
        action_row_top.Add(self.copy_button, 0)
        self.body_sizer.Add(action_row_top, 0, wx.BOTTOM, 8)

        action_row_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self.body, label="Save destination")
        style_button(self.save_button)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        action_row_bottom.Add(self.save_button, 0, wx.RIGHT, 8)

        self.clear_button = wx.Button(self.body, label="Clear point")
        style_button(self.clear_button)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)
        action_row_bottom.Add(self.clear_button, 0)
        self.body_sizer.Add(action_row_bottom, 0)

        self.clear_selection()

    def refresh_message(self):
        self.message.Wrap(rail_wrap_width())
        self.body.Layout()
        self.Layout()
        parent = self.GetParent()
        if parent is not None and hasattr(parent, "FitInside"):
            parent.FitInside()

    def refresh_actions(self):
        self.copy_button.Enable(self.has_selection)
        self.save_button.Enable(self.has_selection)
        self.clear_button.Enable(self.has_selection)
        self.mode_button.SetLabel("Cancel pick" if self.pick_mode_enabled else "Pick course point")
        self.refresh_message()

    def on_toggle_mode(self, event):
        self.GetTopLevelParent().toggle_course_pick_mode()

    def on_copy(self, event):
        self.GetTopLevelParent().copy_map_target_coordinates()

    def on_save(self, event):
        self.GetTopLevelParent().save_map_target_as_destination()

    def on_clear(self, event):
        self.GetTopLevelParent().clear_map_target()

    def set_pick_mode(self, enabled):
        self.pick_mode_enabled = enabled
        if enabled:
            self.message.SetForegroundColour(DashboardTheme.ACCENT)
            self.message.SetLabel("Course mode armed. Click once on the map to place a point.")
        elif self.has_selection:
            self.message.SetForegroundColour(DashboardTheme.SUCCESS)
            self.message.SetLabel("Point active. Drag it to update the course, or click it to cancel.")
        else:
            self.message.SetForegroundColour(DashboardTheme.TEXT_MUTED)
            self.message.SetLabel("Enable course mode to place a point on the map.")
        self.refresh_actions()

    def clear_selection(self):
        self.has_selection = False
        self.coords_value.SetLabel("--")
        self.course_value.SetLabel("--")
        self.distance_value.SetLabel("--")
        if self.pick_mode_enabled:
            self.message.SetForegroundColour(DashboardTheme.ACCENT)
            self.message.SetLabel("Course mode armed. Click once on the map to place a point.")
        else:
            self.message.SetForegroundColour(DashboardTheme.TEXT_MUTED)
            self.message.SetLabel("Enable course mode to place a point on the map.")
        self.refresh_actions()

    def update_selection(self, point, course, distance_nm):
        self.has_selection = True
        self.coords_value.SetLabel(f"{point[0]:.4f}, {point[1]:.4f}")
        self.course_value.SetLabel(f"{course} deg")
        self.distance_value.SetLabel(f"{distance_nm:,} nm")
        self.set_pick_mode(False)
