import cv2
import glob
import os
import os.path as osp

def read_image(params):
    file_path = params['file_path']
    image_files = glob.glob(osp.join(file_path, "*.jpg"))
    for f in image_files:
        img = cv2.imread(f)
        yield img

def do_file_capture(*args, **kwargs):
    params = {}
    outputs = {}
    if kwargs is not None:
        params = kwargs['params']
        outputs = kwargs['outputs']
        img_generator = read_image(params)
        outputs['image'] = next(img_generator)
