#!/usr/bin/python

# Copyright (c) 2009-2015, Dwight Hubbard
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.

# Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>, Phenome Project
# Making small modifications, return TRUE for success instead of FALSE, double check status on cycle, etc.
# For original file, please see https://github.com/dwighthubbard/python-dlipower


"""
Digital Loggers Web Power Switch Management
The module provides a python class named
powerswitch that allows managing the web power
switch from python programs.
When run as a script this acts as a command line utility to
manage the DLI Power switch.
Notes
-----
This module has been tested against the following
Digital Loggers Power network power switches:
  WebPowerSwitch II
  WebPowerSwitch III
  WebPowerSwitch IV
  WebPowerSwitch V
  Ethernet Power Controller III

"""

from __future__ import print_function
from bs4 import BeautifulSoup
import logging
import multiprocessing
import os
import json
import requests
import time
from six.moves.urllib.parse import quote
from phenome_core.core.base.logger import root_logger as logger

# Global settings
TIMEOUT = 3
RETRIES = 2
CYCLETIME = 3
CONFIG_DEFAULTS = {
    'timeout': TIMEOUT,
    'cycletime': CYCLETIME,
    'userid': 'admin',
    'password': '4321',
    'hostname': '192.168.0.100'
}
CONFIG_FILE = os.path.expanduser('~/.dlipower.conf')


def _call_it(params):   # pragma: no cover
    """indirect caller for instance methods and multiprocessing"""
    instance, name, args = params
    kwargs = {}
    return getattr(instance, name)(*args, **kwargs)

class DLIPowerException(Exception):
    """
    An error occurred talking the the DLI Power switch
    """
    pass

class Outlet(object):
    """
    A power outlet class
    """
    use_description = True

    def __init__(self, switch, outlet_number, description=None, state=None):
        self.switch = switch
        self.outlet_number = outlet_number
        self.description = description
        if not description:
            self.description = str(outlet_number)
        self._state = state

    def __unicode__(self):
        name = None
        if self.use_description and self.description:  # pragma: no cover
            name = '%s' % self.description
        if not name:
            name = '%d' % self.outlet_number
        return '%s:%s' % (name, self._state)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return "<dlipower_outlet '%s'>" % self.__unicode__()

    def _repr_html_(self):  # pragma: no cover
        """ Display representation as an html table when running in ipython """
        return u"""<table>
    <tr><th>Description</th><th>Outlet Number</th><th>State</th></tr>
    <tr><td>{0:s}</td><td>{1:s}</td><td>{2:s}</td></tr>
</table>""".format(self.description, self.outlet_number, self.state)

    @property
    def state(self):
        """ Return the outlet state """
        return self._state

    @state.setter
    def state(self, value):
        """ Set the outlet state """
        self._state = value
        if value in ['off', 'OFF', '0']:
            self.off()
        if value in ['on', 'ON', '1']:
            self.on()

    def cycle(self):
        self.switch.off(self.outlet_number)
        time.sleep(CYCLETIME)
        return self.switch.on(self.outlet_number)

    def off(self):
        """ Turn the outlet off """
        return self.switch.off(self.outlet_number)

    def on(self):
        """ Turn the outlet on """
        return self.switch.on(self.outlet_number)

    def rename(self, new_name):
        """
        Rename the outlet
        :param new_name: New name for the outlet
        :return:
        """
        return self.switch.set_outlet_name(self.outlet_number, new_name)

    @property
    def name(self):
        """ Return the name or description of the outlet """
        return self.switch.get_outlet_name(self.outlet_number)

    @name.setter
    def name(self, new_name):
        """ Set the name of the outlet """
        self.rename(new_name)


class PowerSwitch(object):
    """ Powerswitch class to manage the Digital Loggers Web power switch """
    __len = 0

    __current_outlet_status = None

    def __init__(self, userid=None, password=None, hostname=None, timeout=None,
                 cycletime=None, retries=None):
        """
        Class initializaton
        """
        if not retries:
            retries = RETRIES
        config = self.load_configuration()
        if retries:
            self.retries = retries
        if userid:
            self.userid = userid
        else:
            self.userid = config['userid']
        if password:
            self.password = password
        else:
            self.password = config['password']
        if hostname:
            self.hostname = hostname
        else:
            self.hostname = config['hostname']
        if timeout:
            self.timeout = float(timeout)
        else:
            self.timeout = config['timeout']
        if cycletime:
            self.cycletime = float(cycletime)
        else:
            self.cycletime = config['cycletime']
        self._is_admin = True

        # query itself and get the outlets
        self.statuslist()

    def get_outlets(self):

        return self.__current_outlet_status

    def __len__(self):
        """
        :return: Number of outlets on the switch
        """
        if self.__len == 0:
            self.__len = len(self.statuslist())
        return self.__len

    def __repr__(self):
        """
        display the representation
        """
        if not self.statuslist():
            return "Digital Loggers Web Powerswitch " \
                   "%s (UNCONNECTED)" % self.hostname
        output = 'DLIPowerSwitch at %s\n' \
                 'Outlet\t%-15.15s\tState\n' % (self.hostname, 'Name')
        for item in self.statuslist():
            output += '%d\t%-15.15s\t%s\n' % (item[0], item[1], item[2])
        return output

    def _repr_html_(self):
        """
        __repr__ in an html table format
        """
        if not self.statuslist():
            return "Digital Loggers Web Powerswitch " \
                   "%s (UNCONNECTED)" % self.hostname
        output = '<table>' \
                 '<tr><th colspan="3">DLI Web Powerswitch at %s</th></tr>' \
                 '<tr>' \
                 '<th>Outlet Number</th>' \
                 '<th>Outlet Name</th>' \
                 '<th>Outlet State</th></tr>\n' % self.hostname
        for item in self.statuslist():
            output += '<tr><td>%d</td><td>%s</td><td>%s</td></tr>\n' % (
                item[0], item[1], item[2])
        output += '</table>\n'
        return output

    def __getitem__(self, index):
        outlets = []
        if isinstance(index, slice):
            status = self.statuslist()[index.start:index.stop]
        else:
            status = [self.statuslist()[index]]

        if status is not None:
            for outlet_status in status:
                power_outlet = Outlet(
                    switch=self,
                    outlet_number=outlet_status[0],
                    description=outlet_status[1],
                    state=outlet_status[2]
                )
                outlets.append(power_outlet)
        if len(outlets) == 1:
            return outlets[0]
        return outlets

    def load_configuration(self):
        """ Return a configuration dictionary """
        if os.path.isfile(CONFIG_FILE):
            file_h = open(CONFIG_FILE, 'r')
            try:
                config = json.load(file_h)
            except ValueError:
                # Failed
                return CONFIG_DEFAULTS
            file_h.close()
            return config
        return CONFIG_DEFAULTS

    def save_configuration(self):
        """ Update the configuration file with the object's settings """
        # Get the configuration from the config file or set to the defaults
        config = self.load_configuration()

        # Overwrite the objects configuration over the existing config values
        config['userid'] = self.userid
        config['password'] = self.password
        config['hostname'] = self.hostname
        config['timeout'] = self.timeout

        # Write it to disk
        file_h = open(CONFIG_FILE, 'w')
        # Make sure the file perms are correct before we write data
        # that can include the password into it.
        os.fchmod(file_h.fileno(), 0o0600)
        if file_h:
            json.dump(config, file_h, sort_keys=True, indent=4)
            file_h.close()
        else:
            raise DLIPowerException(
                'Unable to open configuration file for write'
            )

    def verify(self):
        """ Verify we can reach the switch, returns true if ok """
        if self.geturl():
            return True
        return False

    def geturl(self, url='index.htm'):
        """ Get a URL from the userid/password protected powerswitch page
            Return None on failure
        """
        full_url = "http://%s/%s" % (self.hostname, url)
        result = None
        request = None
        for i in range(0, self.retries):

            try:
                request = requests.get(full_url, auth=(self.userid, self.password,),  timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                logger.warning("Request to URL {} timed out - {} retries left.".format(full_url, (self.retries - i - 1)))
                logger.debug("Caught exception {}".format(e))
                continue

            if request is not None and request.status_code == 200:
                result = request.content
                break

        if request is not None:
            logger.debug('Request to URL {} - response code: {}'.format(full_url, request.status_code))

        return result

    def determine_outlet(self, outlet=None):
        """ Get the correct outlet number from the outlet passed in, this
            allows specifying the outlet by the name and making sure the
            returned outlet is an int
        """
        outlets = self.statuslist()
        if outlet and outlets and isinstance(outlet, str):
            for plug in outlets:
                plug_name = plug[1]
                if plug_name and plug_name.strip() == outlet.strip():
                    return int(plug[0])
        try:
            outlet_int = int(outlet)
            if outlet_int <= 0 or outlet_int > self.__len__():
                raise DLIPowerException('Outlet number %d out of range' % outlet_int)
            return outlet_int
        except ValueError:
            raise DLIPowerException('Outlet name \'%s\' unknown' % outlet)


    def get_outlet_name(self, outlet=0):
        """ Return the name of the outlet """
        outlet = self.determine_outlet(outlet)
        outlets = self.statuslist()
        if outlets and outlet:
            for plug in outlets:
                if int(plug[0]) == outlet:
                    return plug[1]
        return 'Unknown'

    def set_outlet_name(self, outlet=0, name="Unknown"):
        """ Set the name of an outlet """

        self.__current_outlet_status = None
        self.geturl(
            url='unitnames.cgi?outname%s=%s' % (outlet, quote(name))
        )
        return self.get_outlet_name(outlet) == name

    def off(self, outlet=0):

        """ Turn off a power to an outlet
            NOTE - changed return codes from original version of this file.
            True == Success
            False == Fail
        """

        # get the switch outlet
        switch_outlet = self.determine_outlet(outlet)

        # clear status
        self.__current_outlet_status = None

        self.geturl(url='outlet?%d=OFF' % switch_outlet)
        return self.status(outlet) == 'OFF'

    def on(self, outlet=0):

        """ Turn on power to an outlet
            NOTE - changed return codes from original version of this file.
            True == Success
            False == Fail
        """

        # get the switch outlet
        switch_outlet = self.determine_outlet(outlet)

        # clear status
        self.__current_outlet_status = None

        self.geturl(url='outlet?%d=ON' % switch_outlet)
        return self.status(outlet) == 'ON'

    def cycle(self, outlet=0):
        """ Cycle power to an outlet
            True = Power CYCLE Success
            False = Power off Fail or Power back on Fail
        """
        if self.off(outlet) == False:
            return False

        time.sleep(self.cycletime)
        self.on(outlet)

        # Make sure outlet is ON
        return self.status(outlet) == 'ON'

    def statuslist(self):
        """ Return the status of all outlets in a list,
        each item will contain 3 items plugnumber, hostname and state  """

        if self.__current_outlet_status != None:
            return self.__current_outlet_status

        outlets = []
        url = self.geturl('index.htm')
        if not url:
            return None
        # Get the root of the table containing the port status info
        try:
            soup = BeautifulSoup(url, "html.parser")
            root = soup.findAll('td', text='1')[0].parent.parent.parent
        except IndexError:
            # Finding the root of the table with the outlet info failed
            # try again assuming we're seeing the table for a user
            # account insteaed of the admin account (tables are different)
            try:
                self._is_admin = False
                root = soup.findAll('th', text='#')[0].parent.parent.parent
            except IndexError:
                return None
        for temp in root.findAll('tr'):
            columns = temp.findAll('td')
            if len(columns) == 5:
                plugnumber = columns[0].string
                hostname = columns[1].string
                state = columns[2].find('font').string.upper()
                outlets.append([int(plugnumber), hostname, state])
        if self.__len == 0:
            self.__len = len(outlets)

        # set the current outlets
        self.__current_outlet_status = outlets

        return outlets

    def printstatus(self):
        """ Print the status off all the outlets as a table to stdout """

        outlets = self.statuslist()
        if not outlets:
            print(
                "Unable to communicate to the Web power "
                "switch at %s" % self.hostname
            )
            return None
        print('Outlet\t%-15.15s\tState' % 'Name')
        for item in outlets:
            print('%d\t%-15.15s\t%s' % (item[0], item[1], item[2]))
        return

    def status(self, outlet=1):
        """
        Return the status of an outlet, returned value will be one of:
        ON, OFF, UNKNOWN
        """
        outlet = self.determine_outlet(outlet)
        outlets = self.statuslist()
        if outlets and outlet:
            for plug in outlets:
                if plug[0] == outlet:
                    return plug[2]

        # changed case to match _STATE_ ENUM in Holitics/Phenome platform
        return 'UNKNOWN'

    def command_on_outlets(self, command, outlets):
        """
        If a single outlet is passed, handle it as a single outlet and
        pass back the return code.  Otherwise run the operation on multiple
        outlets in parallel the return code will be failure if any operation
        fails.  Operations that return a string will return a list of strings.
        """

        # since multiple commands are being sent, clear the status
        self.__current_outlet_status = None

        if len(outlets) == 1:
            result = getattr(self, command)(outlets[0])
            if isinstance(result, bool):
                return result
            else:
                return [result]
        pool = multiprocessing.Pool(processes=len(outlets))
        result = [
            value for value in pool.imap(
                _call_it,
                [(self, command, (outlet, )) for outlet in outlets],
                chunksize=1
            )
        ]
        if isinstance(result[0], bool):
            for value in result:
                if value:
                    return True
            return result[0]
        return result


if __name__ == "__main__":
    PowerSwitch().printstatus()