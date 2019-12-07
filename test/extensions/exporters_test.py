# exporters_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys
from phenome.test import BaseTest

CONST_API_PORT = 10000


class TestExporters(BaseTest):

    def setUp(self):

        global CONST_API_PORT

        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        super(TestExporters, self).setUp()

        # start with the base port, we will need to increment for each test as the sockets take a while to clear up
        sys._unit_tests_API_TARGET_PORT = self.CONST_SIMULATOR_API_TARGET_PORT

    def test_001_load_exporters(self):

        pass

    def test_002_STATSD(self):

        # This unit test is testing the statsd client and UDP simuserver more than anything else

        self.CONST_SIMULATOR_API_TARGET_PORT += 1
        api_port = self.CONST_SIMULATOR_API_TARGET_PORT

        response = None
        message = "Hello World"

        # start the simulator
        simulator = self.startSimulator(None, "UDP_SERVER", api_port)

        try:

            import statsd
            c = statsd.StatsClient('localhost', api_port, prefix='phenome')
            c.incr(message)

            # did the UDP server get a Hello World Counter?
            response = simulator.get_last_query().decode()
            self.assertEqual('phenome.Hello World:1|c', response)

            # did the UDP server get a Metric2 Gauge?
            c.gauge("Metric2",100)
            response = simulator.get_last_query().decode()
            self.assertEqual('phenome.Metric2:100|g', response)

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response
