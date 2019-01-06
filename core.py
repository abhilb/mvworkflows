import json
import cv2
import glob

import os.path as osp

from backend.file_capture import do_file_capture
from backend.mean_filter import do_mean_filter
from backend.file_save import do_file_save

TASK_TYPES = []

class TaskBuilder():
    """ Factory class to create Task objects """
    @staticmethod
    def create(task_type):
        if task_type in TASK_TYPES:
            task = Task()

def dummy_func(*args, **kwargs):
    print("dummy")


class Task():
    """Backend representation of a task"""
    def __init__(self, name):
        self._params = {}
        self._inputs = {}
        self._properties = []
        self._func = dummy_func
        self._outputs = {}
        self._id = ''
        self._name = name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        self._id = id_

    @property
    def name(self):
        return self._name

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, inputs):
        self._inputs = inputs

    @property
    def outputs(self):
        return self._outputs

    def set_executor(self, func):
        self._func = func

    def __call__(self):
        return self._func(params = self._params, inputs = self._inputs, outputs = self._outputs)

task_map = {
        'file_capture' : do_file_capture,
        'mean_filter' : do_mean_filter,
        'file_save' : do_file_save
        }

def main():
    with open("Product1.json") as f:
        product = json.load(f)

        workflows = product['workflows']
        wf = workflows[0]

        operators = wf['operators']
        tasks = []
        op_results = {}
        for op in operators:
            task_type = op['operator']
            t = Task(op['name'])
            t.set_executor(task_map[task_type])
            t.params = op['parameters']
            t.inputs = op['inputs']
            t.id = op['id']
            tasks.append(t)

        for t in tasks:
            for k,v in t.inputs.items():
                t.inputs[k] = op_results[v]
            t()
            for key,value in t.outputs.items():
                op_results['/'.join([t.name, key])] = value
            print(op_results.keys())

if __name__ == "__main__":
    main()
