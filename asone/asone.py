import copy
import cv2
from loguru import logger
import numpy as np
import os
import time

import asone
import asone.utils as utils
from asone.trackers import Tracker
from asone.detectors import Detector
from asone.utils.default_cfg import config


class ASOne:
    def __init__(self,
                 detector: int = 0,
                 tracker: int = -1,
                 weights: str = None,
                 use_cuda: bool = True) -> None:

        self.use_cuda = use_cuda

        # get detector object
        self.detector = self.get_detector(detector, weights)

        if tracker == -1:
            self.tracker = None
            return
         
        self.tracker = self.get_tracker(tracker)

    def get_detector(self, detector: int, weights: str):
        detector = Detector(detector, weights=weights,
                            use_cuda=self.use_cuda).get_detector()
        return detector

    def get_tracker(self, tracker: int):

        tracker = Tracker(tracker, self.detector,
                          use_cuda=self.use_cuda)
        return tracker

    def _update_args(self, kwargs):
        for key, value in kwargs.items():
            if key in config.keys():
                config[key] = value
            else:
                print(f'"{key}" argument not found! valid args: {list(config.keys())}')
                exit()
        return config

    def track_stream(
            self, stream_url, **kwargs
    ):

        output_filename = 'result.mp4'
        kwargs['filename'] = output_filename
        config = self._update_args(kwargs)

        for (bbox_details, frame_details, action) in self._start_tracking(stream_url, config):
            # yeild bbox_details, frame_details to main script
            yield bbox_details, frame_details, action

    def track_video(self,
                    video_path,
                    **kwargs
                    ):            
        output_filename = os.path.basename(video_path)
        kwargs['filename'] = output_filename
        config = self._update_args(kwargs)

        for (bbox_details, frame_details, action) in self._start_tracking(video_path, config):
            # yeild bbox_details, frame_details to main script
            yield bbox_details, frame_details, action

    def track_webcam(self,
                     cam_id=0,
                     **kwargs):
        output_filename = 'results.mp4'

        kwargs['filename'] = output_filename
        kwargs['fps'] = 29
        config = self._update_args(kwargs)

        for (bbox_details, frame_details, action) in self._start_tracking(cam_id, config):
            # yeild bbox_details, frame_details to main script
            yield bbox_details, frame_details, action

    def detect(self, source, **kwargs) -> np.ndarray:
        """ Function to perform detection on an img

        Args:
            source (_type_): if str read the image. if nd.array pass it directly to detect

        Returns:
            _type_: ndarray of detection
        """
        if isinstance(source, str):
            source = cv2.imread(source)
        return self.detector.detect(source, **kwargs)

    def _start_tracking(
            self, stream_path: str, config: dict
    ) -> tuple:
        if not self.tracker:
            raise RuntimeError('No tracker is selected. use detect()' +
                               ' function perform detection or pass a tracker.')

        fps = config.pop('fps')
        output_dir = config.pop('output_dir')
        filename = config.pop('filename')
        save_result = config.pop('save_result')
        display = config.pop('display')
        draw_trails = config.pop('draw_trails')
        class_names = config.pop('class_names')

        cap = cv2.VideoCapture(stream_path)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps is None:
            fps = cap.get(cv2.CAP_PROP_FPS)

        if save_result:
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, filename)
            logger.info(f"video save path is {save_path}")
            video_writer = cv2.VideoWriter(
                save_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (int(width), int(height)),
            )

        frame_id = 1
        tic = time.time()
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == asone.ESC_KEY:
                break
            elif key == asone.SPACE_KEY:
                yield "", "", "annotation"

            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("Failed to read video. It either ended or corrupted")
            bboxes_xyxy, ids, scores, class_ids = self.tracker.detect_and_track(
                frame, config)
            elapsed_time = time.time() - start_time
            fps = 1 / elapsed_time
            # logger.info(
            #     f"fps: {fps:.2f} frame: {frame_id}/{int(frame_count)}" +
            #     f"({elapsed_time * 1000:.2f} ms)"
            # )
            if display or save_result:
                im0 = copy.deepcopy(frame)
                cv2.line(im0, (20, 25), (127, 25), [85, 45, 255], 30)
                cv2.putText(im0, f'FPS: {int(fps)}', (11, 35), 0, 1, [
                    225, 255, 255], thickness=2, lineType=cv2.LINE_AA)
                im0 = utils.draw_boxes(im0,
                                       bboxes_xyxy,
                                       class_ids,
                                       identities=ids,
                                       draw_trails=draw_trails,
                                       class_names=class_names)
            if display:
                cv2.imshow('Sample', im0)
            if save_result:
                video_writer.write(im0)
            frame_id += 1
            # yeild required values in form of (bbox_details, frames_details)
            yield (bboxes_xyxy, ids, scores, class_ids), (im0 if display else frame, frame_id-1, frame_count, fps), "stream"
        tac = time.time()
        logger.info(f'Total Time Taken: {tac - tic:.2f}')
