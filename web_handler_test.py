import numpy

from web_handler import frame_array_to_image_data
from proto.generated import detection_handler_pb2


def test_frame_array_to_image_data():
    frame = detection_handler_pb2.float_array(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], shape=[1, 4, 3])
    img_data = frame_array_to_image_data(frame)
    assert img_data == [1, 2, 3, 255, 4, 5, 6, 255, 7, 8, 9, 255, 10, 11, 12, 255]


def test_frame_array_to_image_data_real_data_01():
    msg = detection_handler_pb2.handle_detection_request()
    with open('./samples/detection-requeust-with-frame-01.bin', 'rb') as f:
        msg.ParseFromString(f.read())
    assert len(msg.frame.numbers) == 480000, "the frame is shape[400,400,3]"
    img_data = frame_array_to_image_data(msg.frame)
    assert len(img_data) == 640000, "for each pixel, we are adding an additional number for alpha channel"
    numpy_img = numpy.array(img_data, numpy.int32).reshape((400,400,4))
    assert numpy_img[0][0][3] == 255