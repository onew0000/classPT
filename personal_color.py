import numpy as np
from detect_face import DetectFace
from color_extract import DominantColors
from colormath.color_objects import LabColor, sRGBColor, HSVColor
from colormath.color_conversions import convert_color
import os

# 각 계절의 팔레트와 색상 비교하는 유틸리티 함수
def color_match(color, palette, tolerance=10):
    count = 0
    for reference_color in palette:
        distance = np.linalg.norm(color - reference_color)
        if distance < tolerance:
            count += 1
    return count

# 각 계절별 팔레트
SPRING_LIGHT_PALETTE = [
    [255, 229, 180], [250, 218, 221], [230, 230, 250],
    [245, 245, 220], [240, 128, 128]
]
SPRING_VIVID_PALETTE = [
    [255, 105, 180], [255, 165, 0], [124, 252, 0],
    [255, 255, 0], [0, 191, 255]
]
SUMMER_LIGHT_PALETTE = [
    [255, 204, 204], [173, 216, 230], [230, 230, 250],
    [211, 211, 211], [152, 251, 152]
]
SUMMER_MUTED_PALETTE = [
    [219, 112, 147], [95, 158, 160], [180, 138, 144],
    [169, 169, 169], [128, 128, 0]
]
AUTUMN_MUTED_PALETTE = [
    [255, 140, 0], [139, 69, 19], [165, 42, 42],
    [128, 128, 0], [193, 154, 107]
]
AUTUMN_DEEP_PALETTE = [
    [255, 140, 0], [101, 67, 33], [139, 0, 0],
    [85, 107, 47], [138, 121, 93]
]
WINTER_BRIGHT_PALETTE = [
    [255, 20, 147], [0, 0, 255], [128, 0, 128],
    [0, 255, 0], [255, 255, 0]
]
WINTER_DEEP_PALETTE = [
    [255, 20, 147], [0, 0, 139], [128, 0, 128],
    [0, 100, 0], [105, 105, 105]
]

# 따뜻한 계열과 차가운 계열 판별
def is_warm(lab_b, weights):
    warm_b_std = [11.6518, 11.71445, 3.6484]
    cool_b_std = [4.64255, 4.86635, 0.18735]

    warm_dist = sum(abs(lab_b[i] - warm_b_std[i]) * weights[i] for i in range(len(lab_b)))
    cool_dist = sum(abs(lab_b[i] - cool_b_std[i]) * weights[i] for i in range(len(lab_b)))

    return warm_dist <= cool_dist

# 봄과 가을을 판별하는 함수
def is_spring_or_fall(hsv_s, weights):
    spring_std = [18.59, 30.30, 25.80]
    fall_std = [27.14, 39.75, 37.5]

    spring_dist = sum(abs(hsv_s[i] - spring_std[i]) * weights[i] for i in range(len(hsv_s)))
    fall_dist = sum(abs(hsv_s[i] - fall_std[i]) * weights[i] for i in range(len(hsv_s)))

    return spring_dist <= fall_dist

# 여름과 겨울을 판별하는 함수
def is_summer_or_winter(hsv_s, weights):
    summer_std = [12.5, 21.7, 24.77]
    winter_std = [16.74, 24.83, 31.37]

    summer_dist = sum(abs(hsv_s[i] - summer_std[i]) * weights[i] for i in range(len(hsv_s)))
    winter_dist = sum(abs(hsv_s[i] - winter_std[i]) * weights[i] for i in range(len(hsv_s)))

    return summer_dist <= winter_dist

# 분석 함수
def analysis(imgpath):
    # 얼굴 감지 및 색상 추출
    df = DetectFace(imgpath)
    print(f"Left Cheek: {df.left_cheek}, Right Cheek: {df.right_cheek}")
    face = [df.left_cheek, df.right_cheek, df.left_eyebrow, df.right_eyebrow, df.left_eye, df.right_eye]
    print(f"Face regions: {face}")  # 얼굴 부위 확인
    
    clusters = 3
    colors = []
    for f in face:
        dc = DominantColors(f, clusters)
        dominant_color, _ = dc.getHistogram()
        print(f"Dominant Color: {dominant_color}")  # 추출된 주요 색상 확인
        colors.append(np.array(dominant_color[0]))

    cheek = np.mean([colors[0], colors[1]], axis=0)
    eyebrow = np.mean([colors[2], colors[3]], axis=0)
    eye = np.mean([colors[4], colors[5]], axis=0)
    
    print(f"Cheek: {cheek}, Eyebrow: {eyebrow}, Eye: {eye}")  # 평균 색상 확인

    # 색상 변환 및 값 확인
    lab_b = []
    hsv_s = []
    for color in [cheek, eyebrow, eye]:
        rgb = sRGBColor(color[0], color[1], color[2], is_upscaled=True)
        lab = convert_color(rgb, LabColor)
        hsv = convert_color(rgb, HSVColor)
        print(f"Lab: {lab}, HSV: {hsv}")  # 색상 변환 결과 확인
        lab_b.append(float(format(lab.lab_b, ".2f")))
        hsv_s.append(float(format(hsv.hsv_s, ".2f")) * 100)

    print(f"Lab B Values: {lab_b}, HSV S Values: {hsv_s}")  # 변환된 Lab B, HSV S 값 확인

    # 따뜻한 계열/차가운 계열 판별
    lab_weights = [30, 20, 5]
    hsv_weights = [10, 1, 1]

    warm = is_warm(lab_b, lab_weights)
    print(f"Is warm tone: {warm}")  # 따뜻한 톤인지 확인

    if warm:
        if is_spring_or_fall(hsv_s, hsv_weights):
            match_spring_light = color_match(cheek, SPRING_LIGHT_PALETTE)
            match_spring_vivid = color_match(cheek, SPRING_VIVID_PALETTE)
            print(f"Spring Light Match: {match_spring_light}, Spring Vivid Match: {match_spring_vivid}")
            if match_spring_light >= match_spring_vivid:
                return '봄 라이트'
            else:
                return '봄 비비드'
        else:
            match_autumn_muted = color_match(cheek, AUTUMN_MUTED_PALETTE)
            match_autumn_deep = color_match(cheek, AUTUMN_DEEP_PALETTE)
            print(f"Autumn Muted Match: {match_autumn_muted}, Autumn Deep Match: {match_autumn_deep}")
            if match_autumn_muted >= match_autumn_deep:
                return '가을 뮤트'
            else:
                return '가을 딥'
    else:
        if is_summer_or_winter(hsv_s, hsv_weights):
            match_summer_light = color_match(cheek, SUMMER_LIGHT_PALETTE)
            match_summer_muted = color_match(cheek, SUMMER_MUTED_PALETTE)
            print(f"Summer Light Match: {match_summer_light}, Summer Muted Match: {match_summer_muted}")
            if match_summer_light >= match_summer_muted:
                return '여름 라이트'
            else:
                return '여름 뮤트'
        else:
            match_winter_bright = color_match(cheek, WINTER_BRIGHT_PALETTE)
            match_winter_deep = color_match(cheek, WINTER_DEEP_PALETTE)
            print(f"Winter Bright Match: {match_winter_bright}, Winter Deep Match: {match_winter_deep}")
            if match_winter_bright >= match_winter_deep:
                return '겨울 브라이트'
            else:
                return '겨울 딥'
            