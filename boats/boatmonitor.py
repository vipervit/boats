import argparse
import sys

import wx
from geopy.distance import distance

from boats.lib.boat import Boat
from boats.lib.common import calc_course, curr_time, get_destination_coordinates, get_version_from_pyproject, miles_to_nautical
from boats.lib.dest import Destinations
from boats.lib.gui.dashboard import ControlsPanel, DestinationPanel, HelmPanel, MapBox, MapPickPanel, PassagePanel, RailHeader, StatusPanel
from boats.lib.gui.theme import DashboardTheme, style_panel
from boats.lib.utimer import UTimer


class Display(wx.Frame):
    def __init__(self, boat_name, version):
        super().__init__(parent=None, title=f"BOATS v{version}")
        self.boat = Boat(boat_name, getdata=True, savetolog=True)
        self.initial_update = True
        self.ts_last_update = None
        self.ts_next_update = None
        self.is_refreshing = False
        self.map_target_point = None
        self.course_pick_mode = False
        self.map_view_center = None

        self.timer = UTimer(self)

        self.shell = wx.Panel(self)
        style_panel(self.shell, DashboardTheme.FRAME_BG, DashboardTheme.TEXT)

        self.box_map = MapBox(self.shell, self.boat.map.mfile, on_map_event=self.handle_map_event)
        self.rail = wx.ScrolledWindow(self.shell, style=wx.VSCROLL)
        style_panel(self.rail, DashboardTheme.FRAME_BG, DashboardTheme.TEXT)
        self.rail.SetScrollRate(0, 20)
        self.rail.SetMinSize((DashboardTheme.RAIL_WIDTH, -1))

        self.header = RailHeader(self.rail, boat_name=boat_name, version=version)
        self.box_status = StatusPanel(self.rail)
        self.box_helm = HelmPanel(self.rail)
        self.box_passage = PassagePanel(self.rail)
        self.box_dest = DestinationPanel(self.rail)
        self.box_map_pick = MapPickPanel(self.rail)
        self.box_controls = ControlsPanel(self.rail)
        self.box_controls.set_zoom(self.boat.map.zoom)
        self.box_controls.set_poll_period(self.timer.period)

        self._build_layout()
        self._configure_frame()
        self.__update_all__(event=None)

        self.Show()

    def _build_layout(self):
        rail_sizer = wx.BoxSizer(wx.VERTICAL)
        rail_sizer.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 4)
        rail_sizer.Add(self.box_status, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.Add(self.box_helm, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.Add(self.box_passage, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.Add(self.box_dest, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.Add(self.box_map_pick, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.Add(self.box_controls, 0, wx.EXPAND | wx.BOTTOM, 12)
        rail_sizer.AddStretchSpacer()
        self.rail.SetSizer(rail_sizer)

        shell_sizer = wx.BoxSizer(wx.HORIZONTAL)
        shell_sizer.Add(self.box_map, 1, wx.EXPAND | wx.ALL, 18)
        shell_sizer.Add(self.rail, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 18)
        self.shell.SetSizer(shell_sizer)

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(self.shell, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

    def _configure_frame(self):
        self.SetMinSize((1180, 760))
        self.SetInitialSize((1520, 920))
        self.Centre()

    def __heartbeat__(self):
        if self.__time_is_up__():
            self.__update_all__(event=None)
        else:
            self.__update_times__()

    def __time_is_up__(self):
        return self.ts_next_update is None or self.ts_next_update <= curr_time()

    def _last_update_timestamp(self):
        return self.boat.log.last_record_timestamp

    def _sync_status_timestamps(self):
        self.ts_last_update = self._last_update_timestamp()
        self.ts_next_update = self.ts_last_update + self.timer.period

    def _flush_status(self):
        self.box_status.update(self.ts_last_update, self.ts_next_update)
        self.box_status.Refresh()
        self.box_status.Update()

    def set_update_state(self, text, tone="neutral"):
        self.box_status.set_state(text, tone)
        self._flush_status()

    def __update_times__(self):
        self._sync_status_timestamps()
        self._flush_status()

    def __update_all__(self, event):
        if self.is_refreshing:
            return

        self.is_refreshing = True
        self.set_update_state("Refreshing data...", "active")

        try:
            self.__update_nav_data__()
            self.__update_panels__()
            self.set_update_state(f"Updated {self.boat.last_update}", "success")
        except Exception as exc:
            self.set_update_state(f"Refresh failed: {exc}", "warning")
        finally:
            self.is_refreshing = False

    def __update_nav_data__(self):
        self.boat.map_zoom = self.box_controls.zoom
        if self.initial_update:
            self.boat.refresh_map()
            self.initial_update = False
        else:
            self.boat.update_from_server()

    def __update_panels__(self):
        self._sync_status_timestamps()
        self._sync_map_target_overlay()
        self.box_map.set_mapfile(self.boat.map.mfile)
        self.box_map.update()
        self.box_dest.update_navigation(speed=self.boat.nav.speed["spd"], pos=self.boat.nav.position)
        self.box_helm.update(self._helm_payload())
        self.box_passage.update(
            last_dist=self.boat.log.last_24_hrs_distance,
            total_days=self.boat.log.total_days,
            total_dist=self.boat.log.total_distance,
        )
        self._flush_status()
        self.rail.FitInside()
        self.Layout()

    def _helm_payload(self):
        return {
            "tws": self.boat.nav.wind["tws"],
            "spd": self.boat.nav.speed["spd"],
            "heel": self.boat.nav.heel,
            "cog": self.boat.nav.az["cog"],
            "ctd": self.box_dest.ctd,
            "sails": self.boat.nav.sailplan,
        }

    def set_polling_interval(self, hrs, mins):
        self.timer.period = hrs * 3600 + mins * 60
        self.box_controls.set_poll_period(self.timer.period)
        self.__update_times__()
        self.set_update_state(f"Polling every {hrs:02d}:{mins:02d}", "active")

    def set_zoom(self, zoom):
        if self.course_pick_mode:
            self.course_pick_mode = False
            self.box_map_pick.set_pick_mode(False)
            self.box_map.set_pick_mode(False)
        self.boat.map_zoom = zoom
        self.boat.map.zoom = zoom
        self.box_controls.set_zoom(zoom)
        self.boat.refresh_map()
        self._sync_map_target_overlay()
        self.box_map.update()
        self.set_update_state(f"Zoom set to {zoom}", "active")

    def _sync_map_target_overlay(self):
        overlay = {"target_pick_enabled": self.course_pick_mode}
        if self.map_view_center is not None:
            overlay["view_center"] = self.map_view_center
        if self.map_target_point is None:
            self.boat.map.set(**overlay)
            self.box_map_pick.clear_selection()
            return

        course = calc_course(self.boat.nav.position, self.map_target_point)
        distance_nm = round(miles_to_nautical(distance(self.map_target_point, self.boat.nav.position).miles))
        overlay.update(
            target_point=self.map_target_point,
            target_line=[self.boat.nav.position, self.map_target_point],
            target_course=course,
        )
        self.boat.map.set(**overlay)
        self.box_map_pick.update_selection(self.map_target_point, course, distance_nm)

    def _sync_view_from_map_event(self, zoom=None, center=None):
        if zoom is None:
            pass
        else:
            self.boat.map_zoom = int(zoom)
            self.boat.map.zoom = int(zoom)
            self.box_controls.set_zoom(int(zoom))
        if center is not None:
            self.map_view_center = (round(center[0], 5), round(center[1], 5))

    def handle_map_event(self, action, payload):
        if action == "pick":
            lat, lon, zoom, center = payload
            self._sync_view_from_map_event(zoom=zoom, center=center)
            self.set_map_target(lat, lon)
        elif action == "clear":
            self.clear_map_target()
        elif action == "cancel-pick":
            zoom, center = payload
            self._sync_view_from_map_event(zoom=zoom, center=center)
            self.course_pick_mode = False
            self.box_map_pick.set_pick_mode(False)
            self.box_map.set_pick_mode(False)
            self.set_update_state("Course mode cancelled during zoom", "neutral")
        elif action == "view-state":
            zoom, center = payload
            self._sync_view_from_map_event(zoom=zoom, center=center)

    def toggle_course_pick_mode(self):
        if self.map_target_point is not None:
            self.set_update_state("Clear the current point before picking a new one", "active")
            return
        self.course_pick_mode = not self.course_pick_mode
        self.box_map_pick.set_pick_mode(self.course_pick_mode)
        self.box_map.set_pick_mode(self.course_pick_mode)
        if self.course_pick_mode:
            self.set_update_state("Course mode armed: click once on the map", "active")
        else:
            self.set_update_state("Course mode cancelled", "neutral")

    def set_map_target(self, lat, lon):
        self.course_pick_mode = False
        self.box_map_pick.set_pick_mode(False)
        self.box_map.set_pick_mode(False)
        self.map_target_point = (round(lat, 5), round(lon, 5))
        self._sync_map_target_overlay()
        self.box_map.set_mapfile(self.boat.map.mfile)
        self.box_map.update()
        course = calc_course(self.boat.nav.position, self.map_target_point)
        self.set_update_state(f"Map point selected: {course} deg", "active")

    def clear_map_target(self):
        if self.map_target_point is None:
            return
        self.course_pick_mode = False
        self.box_map_pick.set_pick_mode(False)
        self.box_map.set_pick_mode(False)
        self.map_target_point = None
        self.boat.refresh_map()
        self._sync_map_target_overlay()
        self.box_map.set_mapfile(self.boat.map.mfile)
        self.box_map.update()
        self.set_update_state("Map point cleared", "neutral")

    def copy_map_target_coordinates(self):
        if self.map_target_point is None:
            self.set_update_state("No map point selected", "warning")
            return
        text = f"{self.map_target_point[0]:.5f}, {self.map_target_point[1]:.5f}"
        if not wx.TheClipboard.Open():
            self.set_update_state("Clipboard unavailable", "warning")
            return
        wx.TheClipboard.SetData(wx.TextDataObject(text))
        wx.TheClipboard.Close()
        self.set_update_state("Coordinates copied to clipboard", "success")

    def save_map_target_as_destination(self):
        if self.map_target_point is None:
            self.set_update_state("No map point selected", "warning")
            return

        dialog = wx.TextEntryDialog(self, "Enter a name for the picked point.", "Save destination")
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            name = dialog.GetValue().strip()
        finally:
            dialog.Destroy()

        if not name:
            self.set_update_state("Destination name required", "warning")
            return

        result = Destinations().add_new(name, [self.map_target_point[0], self.map_target_point[1]])
        if result == -1:
            self.set_update_state("Destination already exists", "warning")
            return

        self.box_dest.reload_saved_destinations(selected_name=name)
        self.set_update_state(f"Saved destination: {name}", "success")

    def apply_destination(self, name):
        if not name:
            self.box_dest.show_lookup_error("blank")
            self.set_update_state("Destination name required", "warning")
            return

        coords = get_destination_coordinates(name)
        if coords is False:
            self.box_dest.show_lookup_error(name)
            self.box_dest.update_navigation(speed=self.boat.nav.speed["spd"], pos=self.boat.nav.position)
            self.box_helm.update(self._helm_payload())
            self.set_update_state("Destination lookup failed", "warning")
            return

        self.box_dest.activate_destination(name, coords)
        self.boat.nav.wpt = coords
        self.boat.refresh_map()
        self._sync_map_target_overlay()
        self.box_map.update()
        self.box_dest.update_navigation(speed=self.boat.nav.speed["spd"], pos=self.boat.nav.position)
        self.box_helm.update(self._helm_payload())
        self.set_update_state(f"Destination set: {name}", "success")


def main(args):
    parser = argparse.ArgumentParser(description="Displays the current boat position, sails, nav, and other data.")
    parser.add_argument("--boat_name")
    args = parser.parse_args(args)

    app = wx.App()
    Display(boat_name=args.boat_name, version=get_version_from_pyproject())
    app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
