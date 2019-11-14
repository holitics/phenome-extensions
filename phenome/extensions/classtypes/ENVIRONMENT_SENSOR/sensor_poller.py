# sensor_poller.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import threading
from phenome_core.core.base.base_poller import BasePoller

# init the poll counter
poll_count = 0

poller_results_class = "phenome.extensions.classtypes.ENVIRONMENT_SENSOR.sensor_results.SensorResults"
poller_process_class = "phenome_core.core.base.base_processor.BaseProcessor"

"""

SensorPoller subclass, based on BasePoller.

"""


class SensorPoller(BasePoller):

    def __init__(self):
        super(SensorPoller, self).__init__(__name__, poller_results_class, poller_process_class, 10)
        self._stop_event = threading.Event()

    def run(self):
        super(SensorPoller, self).run()
