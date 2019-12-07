# phenome_002_exporters_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import time
from phenome.test import BaseTest
from phenome.extensions.exporters.statsd import StatsD
from phenome.test.supporting.test_results import BaseResultsTest

CONST_API_PORT = 7100

class TestExporters(BaseTest):

    def setUp(self):

        global CONST_API_PORT
        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        super(TestExporters, self).setUp()

    def __get_object(self, id):

        from phenome.test.supporting.test_mockobject import MockObject
        object = MockObject()
        object.id = id

        return object

    def _check_simulator_message(self, simulator, message):

        # did the UDP server get the message?
        response = simulator.get_last_query()
        if response is not None:
            self.assertEqual(message, response.decode())
        else:
            msgs = simulator.get_messages_received()
            found_msg = False
            if len(msgs) > 0:
                for msg in msgs:
                    if msg.decode() == message:
                        found_msg = True
                        break

            self.assertTrue(found_msg)

    def test_001_STATSD_Exporter(self):

        # This test will create a StatsD Exporter, test that the Exporter worked using a UDP simulator
        # and will also test the integrity of the EDRs that were exported

        MESSAGE = 'phenome.TEST_RESULTS.ROOT_OBJECT.127-0-0-1.temperature:50|g'

        config = {
            "id": "STATSD_Exporter",
            "metric_prefix": "phenome",
            "metric_pattern": "<MODEL_CLASSTYPE>.<OBJECT_MODEL>.<OBJECT_IP>.<METRIC_ID>",
            "enabled": "True",
            "host": "localhost",
            "port": self.api_port
        }

        # create a StatsD Exporter and test the metric collection
        exporter = StatsD(config)
        results = BaseResultsTest()
        response = None

        # set a test value
        results.set_result(self.__get_object(1),'temperature',50)

        # NEXT - We setup a STATSD Simulator
        simulator = self.startSimulator(None, "UDP_SERVER", self.api_port)
        time.sleep(1)

        try:

            # export to StatsD Daemon and wait a sec - do this TWICE to force flush (sometimes needed)
            exporter.export(results)
            exporter.export(results)
            exporter.export(results)
            time.sleep(1)

            self._check_simulator_message(simulator, MESSAGE)

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response the simulator received with what was sent to statsD

        # Now test the exported EDRs
        edrs = exporter.exported_records
        self.assertTrue(len(edrs)==1)
        self.assertTrue(edrs[0].key=='TEST_RESULTS.ROOT_OBJECT.127-0-0-1.temperature')
        self.assertTrue(edrs[0].metric=='temperature')
        self.assertTrue(edrs[0].value==50)


