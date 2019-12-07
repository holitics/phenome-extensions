# phenome_002_exporters_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import time
from phenome.test import BaseTest
from phenome.extensions.exporters.statsd import StatsD
from phenome.test.supporting.test_results import BaseResultsTest


class TestExporters(BaseTest):

    def setUp(self):
        super(TestExporters, self).setUp()

    def __get_object(self, id):

        from phenome.test.supporting.test_mockobject import MockObject
        object = MockObject()
        object.id = id

        return object

    def test_001_STATSD_Exporter(self):

        # This test will create a StatsD Exporter, test that the Exporter worked using a UDP simulator
        # and will also test the integrity of the EDRs that were exported

        self.CONST_SIMULATOR_API_TARGET_PORT += 1
        api_port = self.CONST_SIMULATOR_API_TARGET_PORT

        config = {
            "id": "STATSD_Exporter",
            "metric_prefix": "phenome",
            "metric_pattern": "<MODEL_CLASSTYPE>.<OBJECT_MODEL>.<OBJECT_IP>.<METRIC_ID>",
            "enabled": "True",
            "host": "localhost",
            "port": api_port
        }

        # create a StatsD Exporter and test the metric collection
        exporter = StatsD(config)
        results = BaseResultsTest()

        # set a test value
        results.set_result(self.__get_object(1),'temperature',50)

        # NEXT - We setup a STATSD Simulator
        response = None

        # start the simulator and wait a sec
        simulator = self.startSimulator(None, "UDP_SERVER", api_port)
        time.sleep(1)

        try:

            # export to StatsD Daemon and wait a sec - do this TWICE to force flush (sometimes needed)
            exporter.export(results)
            exporter.export(results)
            time.sleep(1)

            # did the UDP server get the exported record?
            response = simulator.get_last_query().decode()

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response the simulator received with what was sent to statsD
        self.assertEqual('phenome.TEST_RESULTS.ROOT_OBJECT.127-0-0-1.temperature:50|g', response)

        # Now test the exported EDRs
        edrs = exporter.exported_records
        self.assertTrue(len(edrs)==1)
        self.assertTrue(edrs[0].key=='TEST_RESULTS.ROOT_OBJECT.127-0-0-1.temperature')
        self.assertTrue(edrs[0].metric=='temperature')
        self.assertTrue(edrs[0].value==50)


