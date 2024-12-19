from collections import OrderedDict
import numpy as np
import cv2
import argparse
import dlib
import imutils


facial_features_cordinates = {}

FACIAL_LANDMARKS_INDEXES = OrderedDict([
    ("Mouth", (48, 68)),
    ("Right_Eye", (36, 42)),
     ("Left_Eye", (42,48)),
    ("Right_Cheek", (1, 5)),
    ("Left_Cheek", (12, 16)),
    ("Forehead", (19, 24))
    
])


def shape_to_numpy_array(shape, dtype="int"):
    coordinates = np.zeros((68, 2), dtype=dtype)

    for i in range(0, 68):
        coordinates[i] = (shape.part(i).x, shape.part(i).y)

    return coordinates
def extract_average_color(image, pts):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts, 1)
    mean_color = cv2.mean(image, mask=mask)[:3]
    return mean_color

def visualize_facial_landmarks(image, shape, colors=None, alpha=0.75):
    overlay = image.copy()
    output = image.copy()
    
    ave_color = []

    if colors is None:
        colors = [
                  (168, 100, 168), (158, 163, 32),
                  (163, 38, 32), (180, 42, 220)]

    for (i, name) in enumerate(FACIAL_LANDMARKS_INDEXES.keys()):

        (j, k) = FACIAL_LANDMARKS_INDEXES[name]

        pts = shape[j:k]
        facial_features_cordinates[name] = pts

        hull = cv2.convexHull(pts)
        cv2.drawContours(overlay, [hull], -1, colors[i], -1)
        avg_color = extract_average_color(image, hull)
        ave_color.append(avg_color)
        print(f"Average color for {name}: {avg_color}")
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    print(facial_features_cordinates)
    return ave_color


def get_skin_color(image, shape):
    forehead_points = shape[19:24]
    right_cheek_points = shape[1:5]
    left_cheek_points = shape[12:16]

    forehead_color = extract_average_color(image, forehead_points)
    right_cheek_color = extract_average_color(image, right_cheek_points)
    left_cheek_color = extract_average_color(image, left_cheek_points)
    skin_colors=[forehead_color, right_cheek_color,left_cheek_color]
    skin_color = [0]
    for i in range(0,3):
        skin_color[0] += skin_colors[i]
    skin_color[0] = skin_color[0]/3
    return list( skin_color)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
op_data=[]

for g in range(1, 6):
    image = cv2.imread(f'image_{g}.jpg')

    image = imutils.resize(image, width=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 1)
    print(len(rects))


    for (i, rect) in enumerate(rects):
        shape = predictor(gray, rect)
        shape = shape_to_numpy_array(shape)
        output = visualize_facial_landmarks(image, shape)
        skin_color = get_skin_color(image, shape)
        output = output + skin_color
        op_data.append(output)
