# base_sensor.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject

"""

BaseSensor class. Based on PoweredObject.

"""


class BaseSensor(PoweredObject):

    def __init__(self):
        super(BaseSensor, self).__init__()

    def poll(sensor, results):
        pass
