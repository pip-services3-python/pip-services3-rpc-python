# -*- coding: utf-8 -*-

import datetime

from pip_services3_commons.convert import StringConverter

from .RestOperations import RestOperations


class HeartBeatOperations(RestOperations):
    def __init__(self):
        super(HeartBeatOperations, self).__init__()

    def get_heart_beat_operation(self):
        return lambda req, res: self.heartbeat(req, res)

    def heartbeat(self, req=None, res=None):
        result = StringConverter.to_string(datetime.datetime.now())
        return self._send_result(result)
