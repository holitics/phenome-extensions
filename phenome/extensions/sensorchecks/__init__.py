# __init__.py (for sensorchecks), Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from .ping import PingCheck


def check_pingable(object, collector):

    pinger = PingCheck()
    pinger.set_arguments({'object': object, 'results': collector, 'id': 'ping'})
    pingable = pinger.execute()
    if pingable == False:
        # finish the action
        pinger.finish()

    return pingable

