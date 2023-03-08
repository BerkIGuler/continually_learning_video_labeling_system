from asone import ASOne
import asone
import cfg
from loguru import logger


def setup_tracker(real_time, video_path):

    dt_obj = setup_detector()
    if real_time:
        track_fn = dt_obj.track_webcam(
            0, output_dir="./temp", save_result=cfg.config["SAVE_ORIGINAL"],
            display=cfg.config["DISPLAY_ORIGINAL"],
            filter_classes=cfg.config["FILTERED_CLASSES"])
        logger.info("Real time operating mode...")
    else:
        track_fn = dt_obj.track_video(
            video_path, output_dir="./temp", save_result=cfg.config["SAVE_ORIGINAL"],
            display=cfg.config["DISPLAY_ORIGINAL"],
            filter_classes=cfg.config["FILTERED_CLASSES"])
        logger.info("Video operating mode...")
    return track_fn


def setup_detector():
    detector = dt_obj = ASOne(
        tracker=asone.DEEPSORT,
        detector=asone.YOLOV7_PYTORCH,
        use_cuda=True)
    return  detector
