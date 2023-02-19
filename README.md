# Continually Learning Video Labeling Annotation Tool
## 1) To use custom weights:
### Either
- Change model flag in asone/__init__.py
```
YOLOV7_CUSTOM_1: 82
YOLOV7_CUSTOM_2: 83
YOLOV7_CUSTOM_3: 84
```
- Change asone/detectors/utils/weights_path.py
```
            '82': os.path.join('yolov8','weights','yolo1.onnx'),
            '83': os.path.join('yolov8','weights','yolo2.pt'),
            '84': os.path.join('yolov8','weights','yolo3.onnx')
```
- Initialize ASOne with weights flag
```
dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True,
    weights=YOLOV7_CUSTOM_1)
```
### Or
- Pass either .onnx or .pt weights path directly as flag
```
dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True,
    weights=custom_yolo_weights.pt)
```

## 2) Tracker Selection
- To deactivate the tracker 
```
dt_obj = ASOne(
    tracker=-1,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True,
    weights=custom_yolo_weights.pt)
```

## 3) To Change Input Source
- use one of {track_video, track_stream, track_webcam} methods to
initialize the tracker 
```
track_fn = dt_obj.track_webcam(
    video_path, output_dir="./temp", save_result=cfg.config["SAVE_ORIGINAL"],
    display=cfg.config["DISPLAY_ORIGINAL"],
    filter_classes=cfg.config["FILTERED_CLASSES"])
```
