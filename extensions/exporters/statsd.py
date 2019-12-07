# statsd.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

from phenome_core.core.base.base_exporter import BaseExporter
import statsd


class StatsD(BaseExporter):

    def __init__(self, config):
        super(StatsD, self).__init__(config)

    def export(self, collector):

        port = int(self.config.get('port'))
        host = self.config.get('host')
        prefix = self.config.get('metric_prefix')
        pattern = self.config.get('metric_pattern')

        # get the results as a list of EDRs
        edrs = self.build_metric_collection(pattern, collector)

        exported = []

        try:
            if edrs is not None and len(edrs)>0:

                # create a statsd client
                c = statsd.StatsClient(host, port, prefix=prefix)

                # send to statsD
                for edr in edrs:
                    try:
                        result = edr.value
                        if isinstance(result, str):
                            result = float(result)
                        c.gauge(edr.key, result)

                        # add to the exported list
                        exported.append(edr)

                    except Exception as ex:
                        print(ex)

        except Exception as ex:
            pass

        self.exported_records = exported