# powered_object.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.database.model.object import Object
from phenome_core.core.base.base_object import BaseObject
from phenome_core.util import time_functions, network
from phenome_core.core.helpers import config_helpers
from phenome_core.core.helpers.numeric_helpers import is_number
from phenome_core.core.constants import DEVICE_WAKE_ON_LAN_TIMEOUT_MS
from phenome_core.core.globals import global_enums
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.handlers import message_handler

import sys, logging

"""

Phenome PoweredObject Extension, based on BaseObject.

    All powered objects should subclass this object.

    Provides access to underlying power states, connected PDUs, 
    and commands like restart, reset, power on, power off, etc.
    
"""


class PoweredObject(BaseObject):

    notify_on_power_change = False

    def __init__(self):

        super(PoweredObject, self).__init__()

        # this is a powered object
        self.is_powered = True

        # default to INFO
        self.log_level = logging.INFO

        # should we notify each time the POWER is ON/OFF/CYCLE
        self.notify_on_power_change = config_helpers.get_config_value(
                        "MISC", "notify_on_power_change", True)

        # TODO - move these out of main class

        self.STATES = global_enums.get_enum('_STATE_TYPES_')
        self.STATES_REV = global_enums.get_reverse_map_enum('_STATE_TYPES_')

        self.CONST_STATE_OFF = self.STATES['OFF'].value
        self.CONST_STATE_ON = self.STATES['ON'].value
        self.CONST_STATE_CYCLE = self.STATES['CYCLE'].value
        self.CONST_STATE_UNKNOWN = self.STATES['UNKNOWN'].value

    def _get_power_state_int(self, state_string):

        try:
            power_state = self.STATES[state_string].value
        except:
            power_state = self.CONST_STATE_UNKNOWN

        return power_state

    def set_enabled(self, enabled):

        """
        Sets a powered object's Administrative State

        Returns:
            None
        """

        super(PoweredObject, self).set_enabled(enabled)

        if not enabled and self.admin_disabled:
            if self.__determine_powered_state() == self.CONST_STATE_ON:
                self.__poweroff("Administratively Disabled")

    def is_plugged_into(self, pdu, outlet=None):

        """
        Determines whether a powered object is plugged into a PDU.
        Specifying the outlet number will also check the outlet.

        Returns:
            True if plugged in
            False if not plugged in
        """

        if pdu is not None:
            connected_pdu = self.__get_connected_pdu
            if connected_pdu is not None and connected_pdu == pdu:
                if outlet is not None:
                    return self.connected_outlet == outlet
                else:
                    return True

        return False

    def has_power_source(self):

        """
        Returns if a powered object has a configured power source.

        Returns:
            True - if there is a configured power source
            False - if there is not a configured power source
        """

        pdu = None

        try:
            pdu = self.__get_connected_pdu()
        except Exception as ex:
            self.power_state = self.CONST_STATE_UNKNOWN

        return pdu is not None

    def plug_into(self, power_object, outlet=None):

        """
        "Plugs" an object to a configured power source.

        Returns:
            True - if the relationship is created between object and power source
            False - if the object cannot be "plugged" into the power source
        """

        if power_object:
            self.add_relation(power_object, 1000, outlet)
            if outlet:
                return self.has_relation(power_object) and self.connected_outlet == outlet
            else:
                return self.has_relation(power_object)

        return False

    def _check_outlet_string(self, outlet_str):

        outlets = outlet_str.split(',')
        ok = True
        for outlet in outlets:
            if not is_number(outlet):
                ok = False
                break

        return ok

    def add_relation(self, relation, relation_type_id, relation_details):

        """
        Overrides superclass "add_relation" method in order to set the connected outlet, if applicable

        Returns:
            None
        """

        super(PoweredObject, self).add_relation(relation, relation_type_id, relation_details)

        if relation_type_id == 1000 and self._check_outlet_string(relation_details):
            self.connected_outlet = relation_details

    def remove_relation(self, relation, relation_type_id):

        """
        Overrides superclass "remove_relation" method in order to disconnect the connected outlet, if applicable

        Returns:
            None
        """

        super(PoweredObject, self).remove_relation(relation, relation_type_id)

        if relation_type_id == 1000:
            # this is a PLUGGED INTO relation, clear the outlet
            self.connected_outlet = ""

    def is_powered_on(self):

        """
        Determines if the object is Powered ON

        Returns:
            True - if ON
            False - if OFF
        """

        return self.__is_powered_on()

    def is_powered_off(self):

        """
        Determines if the object is Powered OFF

        Returns:
            True - if OFF
            False - if ON
        """

        return self.__is_powered_off()

    def power_on(self, message=None):

        """
        Powers ON the object

        Returns:
            True - if ON
            False - if OFF
        """

        self.__poweron(message)
        return self.__is_powered_on()

    def power_off(self, message=None):

        """
        Powers OFF the object

        Returns:
            True - if OFF
            False - if ON
        """

        self.__poweroff(message)
        return self.__is_powered_off()

    def get_powered_state(self, refresh_state=True):

        """
        Returns the Powered State of the object.
        Please see the ENUM: _STATE_TYPES_ in the system metadata file.

        Returns:
            Integer: _STATE_TYPES_
        """

        # NOTE - make sure all "POWER/PDU/PLUG" subclasses that implement
        # get_powered_state use a short timeout in case of API/UI access.

        if hasattr(self,'connected_outlet'):

            if self.connected_outlet == '':
                # not plugged into anything
                if self.is_pdu and self.health == 0:
                    # assume it is powered ON - but ONLY if the health is OK
                    self.power_state = self.CONST_STATE_ON
                else:
                    self.power_state = self.CONST_STATE_UNKNOWN

                return self.power_state

        if refresh_state:
            # try to get the power state
            self.__determine_powered_state()

        return self.power_state

    def __get_connected_pdu(self):

        # iterate through relations
        pdus = self.get_related_objects_by_classtype('POWER_DISTRIBUTION_UNIT')

        if pdus is None or len(pdus)==0:
            return None

        if len(pdus)>0:
            # should not be possible, but
            pdu = pdus[0]
        else:
            pdu = pdus

        if isinstance(pdu, Object):
            from phenome_core.core.database.model.api import get_object_by_id
            pdu = get_object_by_id(pdu.id)

        return pdu

    def __determine_powered_state(self):

        try:
            pdu = self.__get_connected_pdu()
            if pdu is not None and self.connected_outlet:
                self.power_state = pdu.get_outlet_state(self.connected_outlet)
            elif self.is_pdu and self.health == 0:
                # again, assume it is Powered ON - but this should be set by the Poller
                self.power_state = self.CONST_STATE_ON

        except Exception as ex:
            logger.error("Could not get outlet state {} on PDU {} - "
                         "ERROR {}".format(self.connected_outlet, pdu.unique_id, ex))
            self.power_state = self.CONST_STATE_UNKNOWN

        return self.power_state

    def __is_powered_on(self):
        return self.power_state == self.CONST_STATE_ON

    def __is_powered_off(self):
        return self.power_state == self.CONST_STATE_OFF

    def __check_for_unit_test(self, desired_value):

        try:
            unit_tests = sys._unit_tests_running
            if unit_tests:
                use_fake_values = sys._unit_tests_use_fake_values
                if use_fake_values:
                    self.power_state = desired_value
                    return True

        except:
            pass

        return False

    def __poweroff(self, message):

        pdu = self.__get_connected_pdu()

        if pdu is None:
            return self.__check_for_unit_test(self.CONST_STATE_OFF)

        result = pdu.power_off_outlets(self.connected_outlet)
        if result is True:
            self.power_state = self.CONST_STATE_OFF
            message = self._get_message("POWER-OFF", None, self, message)
        else:
            message = self._get_message("POWER-OFF", "FAIL", self, message)

        message_handler.log(None, message, self, self.log_level, self.notify_on_power_change)

        return result

    def __poweron(self, message):

        pdu = self.__get_connected_pdu()

        if pdu is None:
            return self.__check_for_unit_test(self.CONST_STATE_ON)

        result = pdu.power_on_outlets(self.connected_outlet)

        if result:

            # set the state
            self.power_state = self.CONST_STATE_ON

            # reset the init state so state machine does not try to auto-powercycle, etc.
            self._reset_init_state()

            message = self._get_message("POWER-ON", None, self, message)

        else:
            message = self._get_message("POWER-ON", "FAIL", self, message)

        message_handler.log(None, message, self, self.log_level, self.notify_on_power_change)

        return result

    def __powercycle(self):

        result = False

        pdu = self.__get_connected_pdu()

        if pdu:

            # was there an error message associated with this powercycle command?
            message = None

            try:
                message = self.results.get_last_error_message_by_object(self.id)
            except:
                pass

            previous_state = self.power_state
            self.power_state = self.CONST_STATE_CYCLE

            # try to powercycle outlets

            if self.connected_outlet == "" and pdu.outlets == "1":
                # if the PDU only has a single outlet, and the "connected_outlet" parameter is not set, just do it
                self.connected_outlet = pdu.outlets

            # update the time
            self.last_powercycle_time = time_functions.current_milli_time()

            # increment the count
            self.powercycle_count = self.powercycle_count + 1

            result = pdu.powercycle_outlets(self.connected_outlet)

            if result is True:

                self.power_state = self.CONST_STATE_ON

                # reset the init state so state machine does not try to auto-powercycle, etc.
                self._reset_init_state()
                message = self._get_message("POWERCYCLE", None, self, message)

            else:

                # return to the previous state
                self.power_state = previous_state
                message = self._get_message("POWERCYCLE", "FAILED", self, message)

            message_handler.log(self.results, message, self, self.log_level, self.notify_on_power_change)

        return result

    def _get_message(self, action_description, failure_cause, object, action_trigger):

        if action_trigger is None:
            action_trigger = ""
        else:
            action_trigger = ". TRIGGER REASON: {}".format(action_trigger)

        if failure_cause is None:
            failure_cause = ""
        else:
            failure_cause = " {}".format(failure_cause)

        message = "{}{}: {} (ID={}) {}".format(
            action_description, failure_cause,
            object.unique_id, object.id, action_trigger)

        return message.strip()

    def powercycle(self):

        """
        Attempts to PowerCycle the object.

        Returns:
            True - if power cycled
        """

        # If we are simply powered OFF, then just power ON instead of going
        # through the entire set of checks and then turning OFF / ON

        if self.get_powered_state() == self.CONST_STATE_OFF:
            # just turn it ON
            return self.power_on()

        # BY DEFAULT, CHECK STATE MACHINE - and other PARAMETERS

        if not self.force_action:

            if hasattr(self, 'last_wol_time'):

                # Was this device recently WOL'd??
                # If so, we should wait a little time for the WOL packet to hit and for the system to come back up
                # if it has been a period of time after the WOL packet and the device is still not PINGABLE,
                # then we can try a powercycle

                try_powercycle = self.last_wol_time == 0 or \
                                 (self.last_wol_time > 0 and
                                  (self.last_wol_time + (DEVICE_WAKE_ON_LAN_TIMEOUT_MS / 2)) > time_functions.current_milli_time())

                if not try_powercycle:
                    logger.debug("{}(ID={}) was very recently sent WOL packet. "
                                 "Waiting longer before POWERCYCLE attempt".format(self.unique_id, self.id))
                    return False

            # have we waited enough time to clear the powercycle count?
            if self.powercycle_count > 0:

                max_time_expired = time_functions.get_timeout_expired(
                    self.last_powercycle_time, self.powercycle_max_wait_time * 1000)

                if max_time_expired:
                    # we can clear them
                    self.powercycle_count = 0

            # have we power-cycled too many times?
            if self.powercycle_count >= self.powercycle_max_attempts:

                # should we disable due to too many power cycle attemps?
                disable = config_helpers.get_config_value(
                        "MISC", "device_disable_after_failed_powercycle", True)

                if disable:

                    powered_off = self.__poweroff("powercycled too many times")

                    if powered_off:

                        # disable the device
                        self.set_enabled(False)

                return powered_off

        # try to actually powercycle
        return self.__powercycle()

    def get_power_usage_watts(self):

        """
        Attempts to return power usage in WATTS for this object.

        Returns:
            Integer

        """

        watt_hours = 0

        try:
            # is this already set in the object?
            if hasattr(self, 'power_usage_watts'):
                watt_hours = self.power_usage_watts
                if watt_hours is None:
                    watt_hours = 0
        except:
            pass

        if watt_hours == 0:
            try:
                if hasattr(self, 'connected_outlet'):
                    if self.connected_outlet is not None and len(self.connected_outlet) > 0:
                        # see if we can get it from an attached PDU or SmartPlug
                        # TODO - is there a PDU or smart outlet here? If so, can we get power usage?
                        pass
            except:
                pass

        return watt_hours

    def wake_on_lan(self):

        """
        Attempts to send Magic Packet (WOL) to the object.

        Returns:
            True - if packet is sent

        Note: True is returned only if packet is "sent".
        There is no checking to see if it really worked and the machine woke up because of that packet.

        """

        if self.force_action is False and hasattr(self, 'last_wol_time'):
            wol_timeout = config_helpers.get_config_value("MISC", "device_wake_on_lan_timeout_ms", DEVICE_WAKE_ON_LAN_TIMEOUT_MS)
            recently_sent_wol = not time_functions.get_timeout_expired(self.last_wol_time, wol_timeout)
        else:
            recently_sent_wol = False

        if not recently_sent_wol:
            return self.__wake_on_lan()
        else:
            return False

    def __wake_on_lan(self):

        # send the packet

        result = network.wake_on_lan(self)

        if result:

            # set the last send packet time
            self.last_wol_time = time_functions.current_milli_time()

            # reset the init state so state machine does not try to auto-powercycle, etc.
            self._reset_init_state()

            message = "Sent wake-on-lan packet -> {} (ID={}) on MAC {}".format(self.unique_id, self.id, self.mac)
            message_handler.log(self.results, message, self, self.log_level, True)

        else:
            # Usually WOL will fail as devices must be configured, etc. ... not worth logging or notifying
            #logger.debug("WOL FAIL for object {} (ID={}) on MAC {}".format(self.unique_id, self.id, self.mac))
            pass

        return result


