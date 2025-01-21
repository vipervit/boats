import pytest

from boats.lib.dest import Destinations


class Test_Destinations:

    @pytest.fixture
    def cl_dest(self):
        return Destinations()

    def test_view(self, cl_dest):
        cl_dest.view()

    def test_add_new(self, cl_dest):
        place = 'POINT D'
        cl_dest.add_new(place, [100, 100])
        assert Destinations().df.iloc[-1]['Name'] == place

# TODO Add actual checkpoints
    def test_add_new_already_exists(self, cl_dest):
        assert cl_dest.add_new('POINT D', [None, None]) == -1

    def test_remove(self, cl_dest):
        cl_dest.remove('POINT D')

