import os
import cfg
import annotation


def main():
    cfg.init_config()
    sample_video_path = os.path.join(cfg.config["VIDEO_DIR"], "test_vid.mp4")

    annotation.annotate(is_real_time=True)

    #annotation.annotate_real_time()

if __name__ == "__main__":
    main()
