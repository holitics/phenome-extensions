# pdu_dli.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome.extensions.classtypes.POWER_DISTRIBUTION_UNIT.base_pdu import BasePDU
from phenome.extensions.lib.dlipower import PowerSwitch
from phenome_core.core.base.logger import root_logger as logger

"""

Digital Loggers PDU Extension, based on BasePDU.

Provides an interface to a Digital Loggers Smart/WEB PDU through the dlipower module.
Requires 'username' and 'password' properties in order to log into the switch.
Please see the dlipower module for more details. 

"""


class PDU_DLI_UniversalC13(BasePDU):

    def __init__(self):
        super(PDU_DLI_UniversalC13, self).__init__()

    def poll(self, results):

        """
        Polls a Digital Loggers PDU by connecting to the switch and retrieving outlet information.

        Returns:
            True if we can connect to the switch.
            False if the switch is not available.
        """

        outlets = None
        switch = self._get_switch()

        if switch:
            outlets = switch.get_outlets()
            if outlets:
                self.power_state = self.CONST_STATE_ON

        return (switch is not None) and (outlets is not None)

    def _get_switch(self):

        switch = None

        try:
            switch = PowerSwitch(hostname=self.ip, userid=self.username, password=self.password, cycletime=3)
        except Exception as ex:
            logger.error(ex)

        return switch

    def get_outlets(self):

        """
        Retrieves outlet information.

        Returns:
            List of dicts of outlet details
        """

        states = []
        state_txt = ''
        switch = self._get_switch()
        if switch:
            outlets = switch.get_outlets()
            for outlet in outlets:
                outlet_details = {"id": outlet[0], "outlet": outlet[0], "name": outlet[1], "state_text": outlet[2],
                                  "state": self.STATES[outlet[2]].value}
                states.append(outlet_details)

        return states

    def power_off(self):

        """
        Power OFF all the outlets.

        Returns:
            True if one or more outlets were powered off.
        """

        x = 0
        switch = self._get_switch()
        if switch and switch.get_outlets():
            for outlet in switch:
                if outlet.off():
                    x = x + 1

        return x>0

    def power_on(self):

        """
        Power ON all the outlets.

        Returns:
            True if one or more outlets were powered on.
        """

        x = 0
        switch = self._get_switch()
        if switch and switch.get_outlets():
            for outlet in switch:
                if outlet.on():
                    x = x + 1

        return x>0

    def powercycle_outlets(self, outlets=None):

        """
        Power CYCLE all the outlets.

        Returns:
            True if one or more outlets were power cycled.
        """

        x = 0
        switch = self._get_switch()
        if switch and switch.get_outlets():
            if outlets is None:
                outlets = self.outlets
            outlets = self.get_iterable_outlets(outlets)
            for outlet in outlets:
                switch_outlet = switch[int(outlet)-1]
                if switch_outlet:
                    if switch_outlet.cycle():
                        x = x + 1

        return x>0

    def power_off_outlets(self, outlets):

        """
        Power OFF specific outlets.

        Returns:
            True if one or more outlets were powered off.
        """

        x = 0
        switch = self._get_switch()
        if switch and switch.get_outlets():
            outlets = self.get_iterable_outlets(outlets)
            for outlet in outlets:
                switch_outlet = switch[int(outlet)-1]
                if switch_outlet:
                    if switch_outlet.off():
                        x = x + 1

        return x>0

    def power_on_outlets(self, outlets):

        """
        Power ON specific outlets.

        Returns:
            True if one or more outlets were powered on.
        """

        x = 0
        switch = self._get_switch()
        if switch and switch.get_outlets():
            outlets = self.get_iterable_outlets(outlets)
            for outlet in outlets:
                switch_outlet = switch[int(outlet)-1]
                if switch_outlet:
                    if switch_outlet.on():
                        x = x + 1

        return x>0

    def get_outlet_state(self, outlet):

        """
        Retrieves outlet state

        Returns:
            Integer - _STATE_TYPES_
        """

        switch = self._get_switch()
        if switch and switch.get_outlets():
            # get the outlet status ('ON', 'OFF', UNKNOWN)
            outlet_status = switch.status(outlet)
            # get the correct state value from the states ENUM and return
            return self._get_power_state_int(outlet_status)
        else:
            return self.CONST_STATE_UNKNOWN

    def get_power_consumption(self, outlet):

        """
        Returns Power Consumption - N/A

        Returns:
            Integer - 0
        """

        # cannot get this on DLI :(
        return 0