# bt_ruuvitag.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import time

from phenome_core.core.base.logger import root_logger as logger
from ruuvitag_sensor.ruuvitag import RuuviTag
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from phenome.extensions.classtypes.ENVIRONMENT_SENSOR.base_sensor import BaseSensor
from phenome_core.core.base.base_processor import BaseProcessor
from phenome_core.util.time_functions import current_milli_time

"""

BlueTooth RuuviTag Extension, based on ENVIRONMENT SENSOR.

    NOTE - on LINUX, returns TEST data. Only really works on Raspian:
        https://github.com/ttu/ruuvitag-sensor/blob/master/install_guide_pi.md

    AND! The Raspberry PI must be running BLUEZ:
    sudo apt-get install bluez-hcidump && echo +++ install successful +++

"""

BLUEZ_ERROR_DISPLAYED = False


class BT_RUUVITAG(BaseSensor):

    def __init__(self):
        super(BT_RUUVITAG, self).__init__()

    def poll(sensor, results):

        """
        Polls a RuuviTag using BT

        Returns:
            True
        """

        tag_instance = RuuviTag(sensor.mac)

        # update state from the device
        state = tag_instance.update()

        if state:

            # populate the sensor results
            if state.get('temperature'):
                results.set_result(sensor, 'temperature', state['temperature'])

            if state.get('humidity'):
                results.set_result(sensor, 'humidity', state['humidity'])

            if state.get('pressure'):
                results.set_result(sensor, 'pressure', state['pressure'])

            if state.get('identifier'):
                # This is NOT the configured NAME
                results.set_result(sensor, 'identifier', state['identifier'])

        else:
            results.inactive_sensors.append(sensor)

        return True

# To define a custom processor for a particular Model,
# use the classname plus "_Processor"


class BT_RUUVITAG_Processor(BaseProcessor):

    def __init__(self):
        super(BT_RUUVITAG_Processor, self).__init__()

    def scan(self, collector):

        """
        Scans for RuuviTags using BlueTooth

        Returns:
            None
        """

        logger.debug("Start scan...")

        try:

            tags = self.find_tags()

            # Now, iterate through found tags and put into the collector

            for tag in tags:

                if not collector.has_object(tag):

                    # get data about this tag
                    data = tags[tag]

                    # and place tag into the DB
                    sensor = self.add(tag, data)

                    if sensor:
                        # we have successfully added into the DB
                        collector.populate(sensor)

        except Exception as ex:
            logger.error("Problem during scan: {}".format(ex))

    def add(self, tag, data):

        """
        Adds a RuuviTag to the DB.

        Returns:
            Object: A Phenome Object of class "RuuviTag"
        """

        from phenome_core.core.database.model import api
        from phenome_core.core.helpers.model_helpers import add_object

        sensor = api.get_object_by_mac(tag)

        if sensor:
            return sensor

        # get the model for RuuviTag
        sensor_model = api.get_objectmodel_by_name('SENSOR_RuuviTag')

        # add the RuuviTag
        sensor = add_object('ENVIRONMENT_SENSOR', sensor_model.id, None, tag, tag, None)

        return sensor

    def find_tags(self):

        """
        Find all RuuviTags.

        Returns:
            dict: MAC and state of found sensors

        """

        global BLUEZ_ERROR_DISPLAYED

        logger.debug("Try to find tags...")

        # This is the amount of time to listen for tags - TODO get from config file
        timeout = 10

        tags = {}
        tags_skip = {}

        macs = []
        start = current_milli_time()

        try:

            for data in RuuviTagSensor._get_ruuvitag_datas(macs, timeout):

                if current_milli_time() > (start+(timeout*1000)):
                    break

                if (data[0] in tags) or (data[0] in tags_skip):
                    continue

                logger.debug("Found TAG {}, DATA {}".format(data[0],data[1]))

                data_format = data[1]['data_format']

                if data_format < 4:
                    tags[data[0]] = data[1]
                else:
                    tags_skip[data[0]] = data[1]
                    logger.debug("Skipping data_format 4 tag - polling locks up thread")

        except:
            logger.error("error while finding tags")

        if tags is None or len(tags)==0:
            if not BLUEZ_ERROR_DISPLAYED:
                BLUEZ_ERROR_DISPLAYED = True
                logger.warning("No RuuviTags Found. Verify this is running on Raspian and "
                               "that you have installed BLUEZ: 'sudo apt-get install bluez-hcidump'")

        return tags

