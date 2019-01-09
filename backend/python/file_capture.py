import cv2
import glob
import os
import os.path as osp
import time

def read_image(params):
    file_path = params['file_path']
    image_files = glob.glob(osp.join(file_path, "*.jpg"))
    print(image_files)
    for f in image_files:
        print(f)
        img = cv2.imread(f)
        print(img.shape)
        time.sleep(20)
        yield img
    raise StopIteration

def do_file_capture(*args, **kwargs):
    params = {}
    outputs = {}
    if kwargs is not None:
        params = kwargs['params']
        outputs = kwargs['outputs']
        img_generator = read_image(params)
        outputs['image'] = next(img_generator)

if __name__ == "__main__":
    try:
        while True:
            do_file_capture(params={'file_path' : 'D:\\images'}, outputs = {})
    except:
        println("Done")
