import annotation_temp

# paths
frames_path = "./frames"
labels_path = "./labels"
video_path = "./data/test_vid.mp4"
anno_frames_path = "./annotated_frames"

# vars
FPS = 15
X_SIZE = 800
Y_SIZE = 500

annotation_temp.annotation_from_local_video(
    video_path, FPS, X_SIZE, Y_SIZE,
    frames_path, labels_path, anno_frames_path)
