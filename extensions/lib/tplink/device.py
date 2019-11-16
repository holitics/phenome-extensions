import socket
import json
import struct
import sys

from .protocol import encrypt, decrypt
from phenome_core.core.helpers.socket_helper import receive, send


class TPLinkSmartDevice:

    """An object to represent any TP-Link smart device.

    You may not have to instantiate that object directly.
    """

    DEFAULT_PORT = 9999

    def __init__(self, host, port=DEFAULT_PORT, timeout=3, connect=False):
        """Initialize a new smart device object.

        :param host: `string` host to connect to.
        :param port: `int` port to connect to (default: 9999).
        :param timeout: `int` timeout used for connect/read/write on the socket
                        (in seconds, default: 3).
        :param connect: `bool` whether you want to connect to the plug on
                        instantiation of the class (default: False).
        """
        self.__host = host
        self.__port = port
        self.__timeout = timeout

        self.__socket = None

        if connect:
            self.connect()

    def __enter__(self):
        """Can be use as a context manager.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection.
        """
        self.close()

    @property
    def host(self):
        """Return the smart device host.
        """
        return self.__host

    @property
    def port(self):
        """Return the smart device port.
        """
        return self.__port

    @property
    def socket(self):
        """Return the socket used to connect to the device.

        Use this property with caution.
        """
        return self.__socket

    def connect(self):
        """Establish a connection to the smart device.
        """
        self.__socket = socket.create_connection(
            (self.__host, self.__port), self.__timeout)

    def close(self):
        """Close the connection to the smart device.
        """
        # The connection is closed already
        if self.__socket is None:
            return

        self.__socket.close()
        self.__socket = None

    def send(self, command):
        """Send a command to the smart device.

        :param command: `dict` or `string` containing the command to send.
        """
        if isinstance(command, dict):
            command = json.dumps(command)

        if self._is_unit_test_running():
            # do not encrypt
            send(self.__socket, command)
        else:
            # default
            self.__socket.send(encrypt(command))

    def _is_unit_test_running(self):

        try:
            return sys._unit_tests_running
        except:
            pass

        return False

    def recv(self):

        """Wait for data coming from the smart device.
        """

        if self._is_unit_test_running():
            return receive(self.__socket, 65536)

        # NOW, the real code

        buffer = bytes()
        msg_length = -1

        # The length of each message is stored in the first 4 bytes.
        while True:
            chunk = self.__socket.recv(4096)
            if not chunk:
                continue

            if msg_length < 0:
                msg_length, *_ = struct.unpack('>I', chunk[0:4])

            buffer += chunk

            if (msg_length > 0 and len(buffer) >= msg_length + 4) or not chunk:
                break

        return json.loads(decrypt(buffer[4:]))
