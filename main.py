import os
import cfg
import annotation


def main():
    cfg.init_config()
    sample_video_path = os.path.join(cfg.config["VIDEO_DIR"], "test_vid.mp4")

    if cfg.config["REAL_TIME"]:
        annotation.annotate()
    else:
        annotation.annotate(video_path=sample_video_path)


if __name__ == "__main__":
    main()
