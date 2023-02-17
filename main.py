import annotation
import os

import cfg


def main():
    cfg.init_config()
    # sample_video
    sample_video_path = os.path.join(cfg.config["VIDEO_DIR"], "seckin.mp4")
    annotation.annotation_from_local_video(sample_video_path)


if __name__ == "__main__":
    main()