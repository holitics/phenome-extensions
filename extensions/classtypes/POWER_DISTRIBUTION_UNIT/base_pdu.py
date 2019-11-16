# base_pdu.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys
from phenome_core.core.helpers.numeric_helpers import is_number
from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject
from abc import ABCMeta, abstractmethod
from phenome.extensions.sensorchecks import check_pingable

"""

Phenome BasePDU Extension, based on PoweredObject.

    All PDU objects should subclass this object.

"""


class BasePDU(PoweredObject):

    __metaclass__ = ABCMeta

    def __init__(self):
        super(BasePDU, self).__init__()
        self.is_pdu = True

    def poll(self, results):

        """
        Polls a PDU. SUBCLASSED objects should really contact the PDU itself.
        Successful contact can allow us to set the power_state to ON

        Returns:
            True if polled
            False or -1 if not polled
        """

        # by default (if no code overrides the poll method), just PING it
        pingable = check_pingable(self, results)

        if pingable:
            self.power_state = self.CONST_STATE_ON

        return pingable

    def get_iterable_outlets(self, outlets):

        """
        Gets a list of PDUs outlets

        Returns:
            List
        """

        if isinstance(outlets, list):
            pass
        elif isinstance(outlets, int):
            outlets = [outlets]
        else:
            if isinstance(outlets, str):
                if "," in outlets:
                    outlets = outlets.split(',')
                elif ' ' in outlets:
                    outlets = outlets.split(' ')
                else:
                    outlets = [outlets]

        return outlets

    def __has_outlet(self, outlets):

        if outlets is None or len(outlets)==0:
            return False

        if is_number(outlets):
            return str(outlets) in self.object.outlets

        pdu_outlets = outlets.split(",")
        for outlet in pdu_outlets:
            if outlet in self.object.outlets:
                return True

    def __check_for_unit_test(self):

        try:
            unit_tests = sys._unit_tests_running
            if unit_tests:
                return True
        except:
            pass

        return False

    def powercycle(self):

        """
        PowerCycle an entire PDU.
        SUBCLASSES must implement a POWERCYCLE method for the PDU.

        Returns:
            True if power cycled
            False if not power cycled
        """

        return False

    @abstractmethod
    def powercycle_outlets(self, outlets=None):

        """
        PowerCycle a PDU's outlet. Should powercycle one or more outlets.
        SUBCLASSES must implement real methods

        Returns:
            Boolean
        """

        if outlets and self.__has_outlet(outlets):
            return self.__check_for_unit_test()
        else:
            return False

    @abstractmethod
    def power_off_outlets(self, outlets):

        """
        Power OFF a PDU's outlet(s).
        SUBCLASSES must implement real methods

        Returns:
            Boolean
        """

        if self.__has_outlet(outlets):
            return self.__check_for_unit_test()
        else:
            return False

    @abstractmethod
    def power_on_outlets(self, outlets):

        """
        Power ON a PDU's outlet(s).
        SUBCLASSES must implement real methods

        Returns:
            Boolean
        """

        if self.__has_outlet(outlets):
            return self.__check_for_unit_test()
        else:
            return False

    @abstractmethod
    def get_outlet_state(self, outlet):

        """
        Get outlet state for a PDU's outlet.
        SUBCLASSES must implement real methods
        Should return INT state from global_enums.get_enum('_STATE_TYPES_')

        Returns:
            Integer - _STATE_TYPES_
        """

        return self.CONST_STATE_UNKNOWN

    @abstractmethod
    def get_outlets(self):

        """
        Get outlets a PDU.
        SUBCLASSES must implement real methods

        Should return a list of state dicts (outlet#,name,state_text,state (INT))
        A "STATE DICTIONARY" should always have at the minimum 'state'. The other members are all optional.

        Returns:
            List of dict
        """

        outlet_details = {"id":"0", "outlet":"0", "name":"", "state_text": "UNKNOWN", "state": self.CONST_STATE_UNKNOWN}
        return [outlet_details]

    @abstractmethod
    def get_power_consumption(self, outlet):

        """
        Returns power consumtion for a PDU.
        SUBCLASSES must implement real methods
        Should return INT WATTS for a particular outlet when implemented.

        Returns:
            Integer - Watts
        """

        raise NotImplementedError("get_power_consumption method not implemented")