# phenome_000_metadata_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome.test import BaseTest


class TestMetaData(BaseTest):

    def setUp(self):
        super(TestMetaData, self).setUp()

    def test_metadata_001_system(self):
        self._test_metadata('system.json')

    def test_metadata_002_system_enum_collision(self):
        self._test_enum_collisions(['system.json'])

    def test_metadata_003_system_infrastructure(self):
        self._test_metadata('system_infrastructure.json')

    def test_metadata_004_system_infrastructure_enum_collision(self):
        self._test_enum_collisions(['system_infrastructure.json'])

    def test_metadata_005_system_sensors(self):
        self._test_metadata('system_sensors.json')

    def test_metadata_006_system_sensors_enum_collision(self):
        self._test_enum_collisions(['system_sensors.json'])

    def test_metadata_007_ALL_enum_collistion(self):
        self._test_enum_collisions(['system.json',
                                    'system_infrastructure.json',
                                    'system_sensors.json'])
