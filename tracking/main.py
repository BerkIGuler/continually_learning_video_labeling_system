import asone
from asone import ASOne

from cfg import config

dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True)

# None to track all classes
filter_classes = None

# tracking function
track_fn = dt_obj.track_video(
    'data/test_vid.mp4', output_dir=config["output_dir"],
    save_result=True, display=True,
    filter_classes=filter_classes)

# Loop over track_fn to retrieve outputs of each frame
for bbox_details, frame_details in track_fn:
    bbox_xyxy, ids, scores, class_ids = bbox_details
    frame, frame_num, fps = frame_details
    # Do anything with bboxes here

    print(type(bbox_xyxy))
    print(bbox_xyxy)
