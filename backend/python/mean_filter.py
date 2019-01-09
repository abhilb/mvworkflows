import cv2

def do_mean_filter(*args, **kwargs):
    params = {}
    inputs = {}
    outputs = {}

    if kwargs is not None:
        params = kwargs['params']
        inputs = kwargs['inputs']
        outputs = kwargs['outputs']
        filter_size = int(params['filter_size'])
        image = inputs['image']
        print(image.shape)
        mean_image = cv2.blur(image, (filter_size, filter_size))
        outputs['image'] = mean_image
