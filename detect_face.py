from imutils import face_utils
import numpy as np
import dlib
import cv2
from collections import OrderedDict
class DetectFace:
    def __init__(self, image):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        image='./images/image_1.jpg'
        print(image)
        self.img = cv2.imread(image)
        print(self.img)
        self.right_eyebrow = []
        self.left_eyebrow = []
        self.right_eye = []
        self.left_eye = []
        self.left_cheek = []
        self.right_cheek = []
        self.FACIAL_LANDMARKS_INDEXES = OrderedDict([
            ('right_eyebrow', (17, 22)),
            ('left_eyebrow', (22, 27)),
            ("Right_Eye", (36, 42)),
            ("Left_Eye", (42, 48)),
            ("Right_Cheek", (1, 5)),
            ("Left_Cheek", (12, 16))

        ])
        self.detect_face_part()


    def detect_face_part(self):
        face_parts = [[], [], [], [], [], []]
        rect = self.detector(cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY), 1)[0]
        print(rect)
        shape = self.predictor(cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY), rect)
        shape = face_utils.shape_to_np(shape)

        idx = 0
        for (i,name) in enumerate(self.FACIAL_LANDMARKS_INDEXES.keys()):
            (j, k) = self.FACIAL_LANDMARKS_INDEXES[name]

            face_parts[idx] = shape[j:k]
            idx += 1
        face_parts = face_parts[1:5]


        self.right_eyebrow = self.extract_face_part(face_parts[0])
        self.left_eyebrow = self.extract_face_part(face_parts[1])
        self.right_eye = self.extract_face_part(face_parts[2])
        self.left_eye = self.extract_face_part(face_parts[3])
        self.left_cheek = self.img[shape[29][1]:shape[33][1], shape[4][0]:shape[48][0]]
        self.right_cheek = self.img[shape[29][1]:shape[33][1], shape[54][0]:shape[12][0]]

    def extract_face_part(self, face_part_points):
        (x, y, w, h) = cv2.boundingRect(face_part_points)
        crop = self.img[y:y + h, x:x + w]
        adj_points = np.array([np.array([p[0] - x, p[1] - y]) for p in face_part_points])

        # Create an mask
        mask = np.zeros((crop.shape[0], crop.shape[1]))
        cv2.fillConvexPoly(mask, adj_points, 1)
        mask = mask.astype(bool)
        crop[np.logical_not(mask)] = [255, 0, 0]

        return crop
