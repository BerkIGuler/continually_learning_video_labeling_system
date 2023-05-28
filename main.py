import os
import cfg
import annotation
import warnings


def main():
    warnings.simplefilter("ignore")
    sample_video_path = os.path.join(cfg.config["VIDEO_DIR"], "bilkent_train_3.MOV")

    if cfg.config["REAL_TIME"]:
        annotation.annotate()
    else:
        annotation.annotate(video_path=sample_video_path)


if __name__ == "__main__":
    main()
