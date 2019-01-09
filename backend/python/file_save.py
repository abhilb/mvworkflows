import cv2
import re
from datetime import datetime
import os.path as osp

def do_file_save(*args, **kwargs):
    params = {}
    inputs = {}
    outputs = {}

    if kwargs is not None:
        params = kwargs['params']
        inputs = kwargs['inputs']
        outputs = kwargs['outputs']

        file_path = params['file_path']
        pattern = re.compile(r"[-.:]")
        file_name = pattern.sub("_", str(datetime.now()))
        file_name += '.jpg'

        print(f'{file_name}')

        file_name = osp.join(file_path, file_name)
        cv2.imwrite(file_name, inputs['image'])
