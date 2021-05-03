from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
from datetime import datetime

class TraceRecorder(object):
    def __init__(self,name="ansible",path=None):
        self._file = None
        self.path = path
        if path == None : 
            self.path = os.getcwd()
        file_name = name + "_" + datetime.now().strftime("%y%d%m%H%M%S") + ".trace"
        self.name = os.path.join(self.path,file_name)
        self._file = open(self.name,"w")

    def __enter__(self):
        return self

    @property
    def file(self):
        return self._file

    def __exit__(self):
        self._file.close()

    def write(self,msg):
        self._file.write("{}\n".format(msg))


def get_tracer(name,path):
    key=name + path if path is not None else ""
    if key in get_tracer.context:
        return get_tracer.context[key]
    get_tracer.context[key] = TraceRecorder(name,path)
    return get_tracer.context[key]

get_tracer.context = {}