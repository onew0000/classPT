import cv2
import time
from collections import OrderedDict
import numpy as np
import os
import argparse
import dlib
import imutils
import shutil
from collections import Counter

from personal_color import analysis
def clear_image_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def get_stream_video(image_folder):
    
    clear_image_folder(image_folder)

    
    cam = cv2.VideoCapture(0)
    time.sleep(1)

    frame_count = 0
    max_frames = 8  

    while True:
        success, frame = cam.read()
        if not success:
            break

        frame_count += 1

        
        if frame_count <= max_frames:
            image_filename = os.path.join(image_folder, f'image_{frame_count}.jpg')
            cv2.imwrite(image_filename, frame)

        
        if frame_count > max_frames:
            frame = cv2.flip(frame, 1)  

        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        
        if frame_count <= max_frames:
            time.sleep(0.8)  

    cam.release()



def inferance():
    inference = []
    imgs = os.listdir('./images')  # ./images 폴더의 모든 파일 목록을 가져옴

    for imgpath in imgs:
        # 이미지 경로 설정
        image_full_path = os.path.join('./images', imgpath)

        # analysis 함수로 이미지 분석
        result = analysis(image_full_path)  # 예외 처리 없음
        print(f"Analyzed: {imgpath} -> Result: {result}")
        inference.append(result)  # 결과 리스트에 추가
    
    # 분석된 결과 리스트 출력
    print(f"Inference results: {inference}")

    # 가장 많이 나온 결과 찾기
    cnt = Counter(inference)
    mode = cnt.most_common(1)  # 빈도수가 가장 높은 결과 찾기
    
    return mode[0][0]
