# core_agent.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.database.db import db_session
from phenome.extensions.classtypes.OBJECT.powered_object import PoweredObject
from phenome_core.core.globals import registered_apps
from phenome_core.core.constants import _CORE_AGENT_MODEL_CLASSNAME_


"""

Phenome CoreAgent Extension, based on PoweredObject.

    Contains/Retrieves information about the local core agent.

"""


class CoreAgent(PoweredObject):

    def __init__(self):

        super(CoreAgent, self).__init__()

        from phenome_core.core.database.model.api import get_objectmodel_by_name
        model = get_objectmodel_by_name(_CORE_AGENT_MODEL_CLASSNAME_)

        if model is None:
            logger.error("Model not initialized. Please check JSON/config and DB.")
            return None

        self.model_id = model.id

    def discover(self):
        # TODO - DISCOVER OTHER AGENTS IN LOCAL MESH
        pass

    def update(self):
        # TODO - CHECK IF THERE IS A SOFTWARE UPDATE
        pass

    def get_system_info(self):

        # get the "current" dev stats
        stats = get_device_performance_stats()

        # now add the apps/system versions
        stats['apps'] = registered_apps.get_apps()

        # TODO - RETRIEVE CLUSTER INFO

        return stats

    def process(object, results, notify):

        if object.unique_id == 'SELF':

            stats = get_device_performance_stats()
            results.set_result(object, 'memory_total', stats['memory_total'])
            results.set_result(object, 'memory_util', stats['memory_util'])
            results.set_result(object, 'disk_util', stats['disk_util'])
            results.set_result(object, 'cpu_util', stats['cpu_util'])

        else:

            #TODO - CALL REMOTE API TO GET STATS FOR AGENT
            pass


def get_device_performance_stats():

    import psutil
    # see: http://psutil.readthedocs.io/en/latest/

    du = psutil.disk_usage('/')
    mem = psutil.virtual_memory()

    mem_util = ((mem.available / mem.total) * 100)
    cpu_util = int(psutil.cpu_percent(interval=1))

    return {"memory_total":mem.total, "memory_util":mem_util, "disk_util":du.percent, "cpu_util":cpu_util}


def add(ipaddress, mac, uniqueid):

    from phenome_core.core.database.model.api import create_object, get_objectmodel_by_name, get_object_by_ip_and_model_id
    model = get_objectmodel_by_name(_CORE_AGENT_MODEL_CLASSNAME_)

    if model is None:
        logger.error("Model not initialized. Please check JSON/config and DB.")
        return None

    obj = get_object_by_ip_and_model_id(ipaddress, model.id)

    if obj is None:

        try:

            from sqlalchemy.exc import IntegrityError

            # create a new core agent
            obj = create_object(model.id, ipaddress, mac, uniqueid)

            # commit
            db_session.add(obj)
            db_session.commit()

        except IntegrityError as e:
            db_session.rollback()

    return obj

