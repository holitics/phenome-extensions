# sensor_results.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.base_results import BaseResults, ObjectState


class SensorState(ObjectState):

    def __init__(self):
        super(SensorState, self).__init__()
        self.temp_error = 0


class SensorBaseResults(BaseResults):

    def __init__(self):
        super(SensorBaseResults, self).__init__('ENVIRONMENT_SENSOR')
