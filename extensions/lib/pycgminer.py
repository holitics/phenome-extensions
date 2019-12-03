# pycgminer.py, Copyright (c) 2013 Thomas Sileo: Original Implementation
# This was originally published under the MIT license.
# Please see: https://pypi.python.org/pypi/pycgminer/0.1.1

# Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Updated implementation
# Updated to support multiple ports (to support multiple miner APIs)
# Include support for Python 2+3 (worked in tandem with Anastasios Selalmazidis)

# Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Updated implementation - remove reference to FLASK
# Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Added Unit Test compatibility and logging

import socket, json, sys, logging

from phenome_core.core.helpers.socket_helper import send_json
from phenome_core.core.base.logger import root_logger as logger


class CgminerAPI(object):

    """ Cgminer RPC API wrapper. """

    DEFAULT_PORT = 4028

    def __init__(self, host='localhost', port=4028, payload_command='command', parameter_argument='parameter', encapsulate_args=False):

        self.data = {}
        self.host = host

        # just in case the configuration is empty and sends None, use the default port
        if port is None:
            port = CgminerAPI.DEFAULT_PORT

        self.port = port
        self.payload_command = payload_command
        self.parameter_argument = parameter_argument
        self.encapsulate_args = encapsulate_args
        self.socket_timeout = 3

        try:
            if sys._unit_tests_running:
                self.host = sys._unit_tests_API_TARGET_LOC
                self.port = sys._unit_tests_API_TARGET_PORT
                # nice long timeout to allow for stepping through debugger
                logger.debug("Unit Tests running - setting socket_timeout to 20")
                self.socket_timeout = 20
        except:
            pass

    def set_sockettimeout(self, timeout):
        self.socket_timeout = timeout

    def call(self, command, arg=None):

        """ Initialize a socket connection,
        send a command (a json encoded dict) and
        receive the response (and decode it).
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.socket_timeout)

        try:
            sock.connect((self.host, self.port))
            payload = {self.payload_command: command}

            # first deal with arguments
            if arg is not None:

                # Parameter must be converted to basestring (no int)
                if sys.version_info.major == 2:
                    arg = str(arg)

                if self.encapsulate_args:
                    payload.update({self.parameter_argument: [arg]})
                else:
                    payload.update({self.parameter_argument: arg})

            send_json(sock, payload)

            response = self._receive(sock, 65536)

        except Exception as e:
            # This is ANTMINER SPECIFIC... Horrible.
            if sys.version_info.major == 2:
                return dict({'STATUS': [{'STATUS': 'error', 'description': str(e)}]})
            if sys.version_info.major == 3:
                return dict({'STATUS': [{'STATUS': 'error', 'description': e}]})
        else:
            # ALSO ANTMINER SPECIFIC
            # also add a comma on the output of the `stats` command by replacing '}{' with '},{'
            if response.find("\"}{\"STATS\":"):
                response = response.replace("\"}{\"STATS\":","\"},{\"STATS\":",1)

            # Another bug in Antminer JSON
            # the null byte makes json decoding unhappy
            # TODO - test for NULL byte at end
            if (response.endswith("}") == False):
                response = response[:-1]

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("CALL: {}\nRESPONSE: {}".format(payload, response))

            return json.loads(response)

        finally:
            # sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                if sys.version_info.major == 2:
                    msg += chunk
                if sys.version_info.major == 3:
                    msg += chunk.decode('utf-8')
            else:
                # end of message
                break
        return msg

    def __getattr__(self, command):

        """ Allow us to make command calling methods.

        >>> cgminer = CgminerAPI()
        >>> cgminer.summary()

        """

        def out(arg=None):
            return self.call(command, arg)

        return out
