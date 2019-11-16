# smartplug_tplink.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome.extensions.classtypes.POWER_DISTRIBUTION_UNIT.base_pdu import BasePDU
from phenome.extensions.lib.tplink.plug import TPLinkSmartPlug
from phenome_core.core.base.logger import root_logger as logger

import time

"""

TPLink SmartPlug Extension, based on BasePDU.

Provides an interface to a TP-Link WIFI SmartPlug.

"""


class SMARTPLUG_TPLink(BasePDU):

    # The TPLink WIFI Plug only supports 1 outlet, AFAIK

    def __init__(self):
        super(SMARTPLUG_TPLink, self).__init__()

    def _switch_plug(self, state):

        plug = self._get_plug()
        if plug:
            if state == 0:
                # we want to turn OFF
                result = plug.turn_off()
            else:
                # turn on
                result = plug.turn_on()

            if result:
                info = plug.info()
                relay_state = info['system']['get_sysinfo']['relay_state']
                return relay_state == state

        return False

    def power_off(self):

        """
        Power OFF the outlet.

        Returns:
            True if powered off.
        """

        return self._switch_plug(0)

    def power_on(self):

        """
        Power ON the outlet.

        Returns:
            True if powered on.
        """

        return self._switch_plug(1)

    def powercycle(self):

        """
        Power CYCLE the outlet.

        Returns:
            True if power cycled.
        """

        return self.powercycle_outlets(self.connected_outlet)

    def powercycle_outlets(self, outlets):

        """
        Power CYCLE the outlet.

        Returns:
            True if power cycled.
        """

        # Switch OFF
        switched_off = self._switch_plug(0)

        # force the X second delay but max of 5 seconds
        try:
            delay = self.powercycle_delay
            if delay > 10:
                delay = 10
        except:
            # use a default of 2 seconds
            delay = 2

        time.sleep(delay)

        # Switch back ON
        switched_on = self._switch_plug(1)

        return switched_off and switched_on

    def power_off_outlets(self, outlets):

        """
        Power OFF the outlet.

        Returns:
            True if powered off.
        """

        return self.power_off()

    def power_on_outlets(self, outlets):

        """
        Power ON the outlet.

        Returns:
            True if powered on.
        """

        return self.power_on()

    def poll(self, results):

        """
        Poll the outlet.

        Returns:
            True if the outlet is responding
        """

        plug = self._get_plug()
        if plug:
            # the WIFI plug is responding, therefore itself is powered ON
            self.power_state = self.CONST_STATE_ON
            self.health = 0

        return plug is not None

    def get_outlets(self):

        """
        Return information about the outlet.

        Returns:
            List of dict - single outlet
        """

        state = self.get_outlet_state(None)
        outlet_details = {"id": "1", "outlet": "1", "name": "Outlet Power", "state_text": self.STATES_REV[state], "state": state}

        return [outlet_details]

    def _get_plug(self):

        plug = None

        try:
            # no more than 2 sec timeout to get powered state just in case we are calling from UI/API
            plug = TPLinkSmartPlug(host=self.ip, connect=True, port=self.port, timeout=2)
        except Exception as ex:
            logger.error(ex)

        return plug

    def get_outlet_state(self, outlet=None):

        """
        Retrieves state of the outlet (not the WIFI plug)

        Returns:
            Integer - _STATE_TYPES_
        """

        power_state = self.CONST_STATE_UNKNOWN

        try:

            plug = self._get_plug()

            if plug:
                info = plug.info()
                relay_state = info['system']['get_sysinfo']['relay_state']
                if relay_state == 0:
                    # powered OFF
                    power_state = self.CONST_STATE_OFF
                else:
                    power_state = self.CONST_STATE_ON

        except Exception as ex:
            logger.error(ex)

        return power_state

    def get_power_consumption(self, outlet):

        """
        Returns Power Consumption - N/A

        Returns:
            Integer - 0
        """

        return 0
