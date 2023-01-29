# last_dance


## To do:
- Ensure raw frame names are unique, format:vidname_framenum.jpg 
- Ensure label names are unique, format:vidname_framenum.txt
- label txt files are in normalized yolo form
```
Each text file must fulfill all the properties of the YOLO format text file which are the following:
1. The first element of each row is a class id, then bounding box properties (x, y, width, height). 
2. Bounding box properties must be normalized (0–1).
3. (x, y) should be the mid-points of a box.

Example:
class_id x y w h
class_id x y w h
class_id x y w h
.
.
. 
```