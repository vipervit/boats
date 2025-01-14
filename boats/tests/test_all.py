import os

import pytest

from boats import Maps
from boats import Boat, datasource
from boats import Log
from boats import Map, MapMarker
from boats import Nav

TEST_BOAT_NAME_LOCAL = 'Testboat_Local'
TEST_BOAT_NAME_REMOTE = 'Testboat_Remote'


class Test_Boat:

    @pytest.fixture
    def boatmarker(self):
        return MapMarker(location=[0, 0],
                         heading=0,
                         wind_heading=0,
                         wind_speed=0
                         )

    @pytest.fixture
    def boat_local(self, boatmarker):
        boat = Boat(name=TEST_BOAT_NAME_LOCAL, getdata=False)
        boat.update_from_log()
        yield boat
        boat.map.__delete_folium_html__()

    @pytest.fixture
    def boat_remote(self, boatmarker):
        boat = Boat(name=TEST_BOAT_NAME_REMOTE)
        yield boat
        boat.map.__delete_folium_html__()

    def test_savetolog_is_false_by_default(self, boat_local):
        assert boat_local.nav.savetolog is False

    def test_nav_default_datasource_set_to_remote(self, boat_remote):
        assert boat_remote.nav.datasource == datasource.remote

    def test_cannot_save_to_log_if_local(self, boat_local):
        boat_local.nav.savetolog = True
        with pytest.raises(ValueError):
            boat_local.update_from_log()

    def test_update_local(self, boat_local):
        boat_local.update_from_log()
        rec = boat_local.log.last_record
        assert rec['lat'] == 39.5066
        assert rec['lon'] == -31.41832

    def test_update_remote(self, boat_remote):
        boat_remote.update_from_server()
        nav = boat_remote.nav
        assert nav.heel == 17
        assert nav.speed['spd'] == 4.6
        assert nav.az['hdg'] == 104
        assert nav.sailplan == ['Mainsail', 'Genaker']

    def test_can_access_log(self, boat_local):
        assert boat_local.log.last_record_timestamp == '22-Oct 06:45'

class Test_Nav:
    @pytest.fixture
    def nav_remote(self):
        return Nav(boat_name=TEST_BOAT_NAME_REMOTE, src=datasource.remote)

    @pytest.fixture
    def nav_local(self):
        return Nav(boat_name=TEST_BOAT_NAME_LOCAL, src=datasource.local)

    def test_get_data(self, nav_local, nav_remote):
        # local
        assert nav_local.boatname == TEST_BOAT_NAME_LOCAL
        assert nav_local.heel == 35
        assert nav_local.sailplan == ['Mainsail', 'Nr.2']
        # remote
        assert nav_remote.boatname == TEST_BOAT_NAME_REMOTE
        assert nav_remote.heel == 17
        assert nav_remote.speed['spd'] == 4.6
        assert nav_remote.az['hdg'] == 104
        assert nav_remote.sailplan == ['Mainsail', 'Genaker']

    def test_show_short(self, nav_local):
        nav_local.show()

    def test_record_schema_matches_required_columns(self, nav_local):
        assert list(nav_local.__collect_log_data__().keys()) == nav_local.log.required_columns()


class Test_Log:
    @pytest.fixture()
    def boatlog(self):
        return Log(boat_name=TEST_BOAT_NAME_LOCAL)

    @pytest.fixture()
    def nonexistinglog(self):
        return Log(boat_name='nonexisting')

    def test_read_from_file_non_existing(self, nonexistinglog):
        with pytest.raises(FileNotFoundError) as e_info:
            nonexistinglog.__read_from_file__()
        assert 'Log file does not exist' in str(e_info.value)
        assert nonexistinglog._file in str(e_info.value)

    def test_write_to_file(self, nonexistinglog):
        contents = {'Line1': 'Hello', 'Line2': 'World'}
        nonexistinglog.__write_to_file__(contents)
        assert nonexistinglog.__exists__() == True
        import os
        os.remove(nonexistinglog._file)

    def test_read_from_file_normal(self, boatlog):
        assert type(boatlog.__read_from_file__()) == dict

    def test_get_track(self, boatlog):
        boatlog.__get_track__()
        assert boatlog._track == [
            [39.5066, -31.41832],
            [39.75233, -31.36641],
            [39.81502, -31.35005],
            [39.81502, -31.35005],
            [39.81505, -31.362190000000002],
            [44.44315, -60.33986],
            [44.44315, -60.33986],
            [44.44315, -60.33986],
            [44.44315, -60.33986],
            [44.44315, -60.33986]]

    def test_get_last_record(self, boatlog):
        rec = boatlog.last_record
        assert rec['tws'] == 21.5
        assert rec['spd'] == 5.8
        assert rec['sails'] == ['Mainsail', 'Nr.2']


class Test_Map:

    @pytest.fixture()
    def mymap(self):
        loc = [43.632, -79.387]
        return Map(boat_name=TEST_BOAT_NAME_LOCAL,
                   title='TORONTO HARBOUR',
                   location=loc,
                   zoom_start=15,
                   marker=MapMarker(location=loc,
                                    heading=180,
                                    wind_heading=260,
                                    wind_speed=25
                                    ))

    def test_get_url(self, mymap):
        for m, s in zip(Maps, ['windy', 'i-boating', 'file://', 'opensea']):
            mymap.set(type=m)
            assert s in Map.__get_url__(mymap)

    def test_cannot_have_marker_if_not_folium(self, mymap):
        maps = [m for m in Maps if m != Maps.Folium]
        for maptype in maps:
            with pytest.raises(ValueError) as e_info:
                mymap.set(type=maptype, marker=MapMarker())

    def test_save_folium(self, mymap):
        mymap.__save_folium_html__()
        assert os.path.exists(mymap._mfile)
        # mymap.show(); time.sleep(1)

    def test_delete_folium(self, mymap):
        mymap.__delete_folium_html__()
        assert not os.path.exists(mymap._mfile)
