# ping.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.core.base.healthscore import add_health_score
from phenome_core.util import network

"""

PingCheck Extension. Extends a BaseAction.

This is used by the agent to PING an object and the deal with error handling, logging, healthscore, etc.

"""


class PingCheck(BaseAction):

    def __init__(self):
        super(PingCheck, self).__init__()

    def execute(self):

        """
        Executes a PING test for an object

        Returns:
            True if runs successfully.
        """

        if self.object.ip is None or len(self.object.ip) == 0:
            # not pingable, no IP, so just return TRUE
            # TODO - we should probably throw an exception (i.e. NotSupportedException)
            return True

        # assume pingable
        ping_code = network.ping(self.object.ip, 3, 500)
        pingable = ping_code == 0

        if not pingable:

            self.has_error = True

            if self.object.unique_id != self.object.ip:
                self.error_message = "Object {} (IP={}, ID={}) is not responding to PING - " \
                                     "could be down".format(self.object.unique_id, self.object.ip, self.object.id)
            else:
                self.error_message = "Object {} (ID={}) is not responding to PING - " \
                                     "could be down".format(self.object.ip, self.object.id)

            self.object_states.ping_error = 1
            self.object.last_health_error = "Object Unreachable"
            add_health_score(self.object, self.results, 8)

        return pingable
