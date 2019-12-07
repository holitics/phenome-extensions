# exporters_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys, time
from phenome.test import BaseTest

CONST_API_PORT = 10000


class TestExporters(BaseTest):

    def setUp(self):

        self.CONST_SIMULATOR_API_TARGET_PORT += 1
        super(TestExporters, self).setUp()

    def test_001_STATSD_Client(self):

        # This unit test is testing the statsd client and UDP simuserver more than anything else

        api_port = self.CONST_SIMULATOR_API_TARGET_PORT

        response = None
        message = "Hello World"

        # start the simulator
        simulator = self.startSimulator(None, "UDP_SERVER", api_port)

        try:

            import statsd
            c = statsd.StatsClient('localhost', api_port, prefix='phenome')
            c.incr(message)
            time.sleep(1)

            # did the UDP server get a Hello World Counter?
            response = simulator.get_last_query().decode()
            if response is not None:
                self.assertEqual('phenome.Hello World:1|c', response)

            # did the UDP server get a Metric2 Gauge? (send a couple times this is UDP)
            c.gauge("Metric2",100)
            c.gauge("Metric2",100)
            c.gauge("Metric2",100)
            time.sleep(1)
            response = simulator.get_last_query().decode()
            self.assertEqual('phenome.Metric2:100|g', response)

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response
