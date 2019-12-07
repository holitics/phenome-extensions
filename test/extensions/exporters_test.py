# exporters_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys, time
from phenome.test import BaseTest

CONST_API_PORT = 8000


class TestExporters(BaseTest):

    def setUp(self):

        global CONST_API_PORT
        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        super(TestExporters, self).setUp()

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

    def test_001_STATSD_Client(self):

        # This unit test is testing the statsd client and UDP simuserver more than anything else

        response = None
        MSG_HELLO = "Hello World"
        MSG_STATSD_1 = 'phenome.Hello World:1|c'
        MSG_STATSD_2 = 'phenome.Metric2:100|g'

        # start the simulator
        simulator = self.startSimulator(None, "UDP_SERVER", self.api_port)

        try:

            import statsd
            c = statsd.StatsClient('localhost', self.api_port, prefix='phenome')

            # Now send the messages

            c.incr(MSG_HELLO)
            time.sleep(1)
            self._check_simulator_message(MSG_STATSD_1)

            # did the UDP server get a Metric2 Gauge? (send a couple times this is UDP)
            c.gauge("Metric2",100)
            c.gauge("Metric2",100)
            time.sleep(1)
            self._check_simulator_message(MSG_STATSD_2)

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response
