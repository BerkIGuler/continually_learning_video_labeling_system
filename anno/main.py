import annotation_temp
import os


# paths
cwd = os.getcwd()
frames_path = os.path.join(cwd, "frames")
labels_path = os.path.join(cwd, "labels")
videos_path = os.path.join(cwd, "videos")
anno_frames_path = os.path.join(cwd, "annotated_frames")

# create folders if not exist
os.makedirs(frames_path, exist_ok=True)
os.makedirs(labels_path, exist_ok=True)
os.makedirs(anno_frames_path, exist_ok=True)


# vars
FPS = 15
X_SIZE = 800
Y_SIZE = 500

annotation_temp.annotation_from_local_video(
    videos_path, FPS, X_SIZE, Y_SIZE,
    frames_path, labels_path, anno_frames_path)
