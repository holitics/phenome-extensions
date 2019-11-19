
import sys
from phenome.test import BaseTest

CONST_API_PORT = 9000


class TestSMARTPlugs(BaseTest):

    def setUp(self):

        global CONST_API_PORT
        # increment the port
        CONST_API_PORT = CONST_API_PORT + 1

        # set the port
        self.api_port = CONST_API_PORT

        super(TestSMARTPlugs, self).setUp()

        # start with the base port, we will need to increment for each test as the sockets take a while to clear up
        sys._unit_tests_API_TARGET_PORT = self.CONST_SIMULATOR_API_TARGET_PORT

    def TPLINK_000_LIVE(self):

        # To get this to run automatically, pre-pend with "test_" and run

        # this is not supposed to behave like a unit test since we are querying a real device
        sys._unit_tests_running = False

        from phenome.extensions.lib.tplink import TPLinkSmartPlug
        import time

        # DEFAULTS TO PORT 9999
        device = TPLinkSmartPlug(host='10.1.10.169', connect=False, port=9999)
        device.connect()

        result = device.turn_off()

        time.sleep(1)

        result = device.turn_on()
        info = device.info()
        relay_state = info['system']['get_sysinfo']['relay_state']
        self.assertEqual(relay_state,1)

        self.assertEqual(info['system']['get_sysinfo']['type'],'IOT.SMARTPLUGSWITCH')
        self.assertEqual(info['system']['get_sysinfo']['model'],'HS100(US)')


    def test_TPLINK_001(self):

        # start simulator

        sim_file = 'tplink_hs100.py'

        # get path to data file
        simulator_data_path = self.rootdir + "/phenome/test/extensions/resources/smartplugs/" + sim_file

        # start the simulator
        simulator = self.startSimulator(simulator_data_path, 'JSON_RPC', self.api_port)

        from phenome.extensions.lib.tplink import TPLinkSmartPlug
        import time, json

        # DEFAULTS TO PORT 9999, but we will use the API port
        device = TPLinkSmartPlug(host=self.CONST_SIMULATOR_API_TARGET_LOC, connect=False, port=self.api_port, timeout=60)
        device.connect()
        result = device.turn_off()
        time.sleep(1)

        device.connect()
        result = device.turn_on()
        json_result = json.loads(result)
        self.assertEqual(json_result['system']['set_relay_state']['err_code'],0)

        device.connect()
        info = device.info()

        json_info = json.loads(info)

        relay_state = json_info['system']['get_sysinfo']['relay_state']
        self.assertEqual(relay_state,1)

        self.assertEqual(json_info['system']['get_sysinfo']['type'],'IOT.SMARTPLUGSWITCH')
        self.assertEqual(json_info['system']['get_sysinfo']['model'],'HS100(US)')

