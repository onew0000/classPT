import os
import asyncio
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cv import get_stream_video, inferance, clear_image_folder

app = FastAPI()

# 이미지 폴더 및 정적 파일 설정
IMAGE_FOLDER = './images'
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

# 전역 컨텍스트 변수
global_context = {
    "tone": "보통",
    "temperature": "23",
    "wether": "맑음",
    "location": "알 수 없음"
}

def get_location_by_ip():
    try:
        ip_response = requests.get('https://ipapi.co/json/')
        ip_data = ip_response.json()
        
        return {
            'ip': ip_data.get('ip'),
            'city': ip_data.get('city', '알 수 없음'),
            'region': ip_data.get('region', '알 수 없음'),
            'country': ip_data.get('country_name', '알 수 없음'),
            'latitude': ip_data.get('latitude'),
            'longitude': ip_data.get('longitude')
        }
    except Exception as e:
        print(f"IP 정보를 가져오는 중 오류 발생: {e}")
        return {
            'city': '알 수 없음',
            'latitude': None,
            'longitude': None
        }

def get_naver_weather(location):
    """
    위치 정보를 바탕으로 날씨 정보를 반환하는 함수
    """
    if not location or not location.get('city'):
        return {
            'location': '알 수 없음',
            'temperature': '23',
            'weather': '맑음'
        }
    
    try:
        # 위치 정보가 있다면 해당 위치의 기본 날씨 정보 반환
        return {
            'location': location.get('city', '알 수 없음'),
            'temperature': '23',
            'weather': '맑음'
        }
    except Exception as e:
        print(f"날씨 정보를 가져오는 중 오류 발생: {e}")
        return {
            'location': location.get('city', '알 수 없음'),
            'temperature': '23',
            'weather': '맑음'
        }

def get_weather_info(lat, lon):
    """
    OpenWeatherMap API를 사용하여 날씨 정보를 가져옵니다.
    """
    API_KEY = "8e14464ae8812105e4f106aee4182812"  # API 키는 환경변수로 관리하는 것이 좋습니다.
    
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        return {
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description']
        }
    except Exception as e:
        print(f"날씨 정보를 가져오는 중 오류 발생: {e}")
        return None

@app.get("/initialize", response_class=HTMLResponse)
async def initialize(request: Request):
    clear_image_folder(IMAGE_FOLDER)
    location = get_location_by_ip()
    weather_info = get_naver_weather(location)
    
    global global_context
    global_context.update({
        "location": weather_info['location'],
        "temperature": weather_info['temperature'],
        "wether": weather_info['weather']
    })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        **global_context
    })

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        **global_context
    })

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(get_stream_video(IMAGE_FOLDER), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/detect", response_class=HTMLResponse)
async def start_video(background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(run_inference)
    return templates.TemplateResponse("index.html", {
        "request": request,
        **global_context
    })

async def run_inference():
    try:
        inference_instance = inferance()
        global global_context
        if isinstance(inference_instance, dict):
            global_context["tone"] = inference_instance.get("tone", "보통")
        
        with open('templates/result.txt', 'w', encoding='utf-8') as f:
            f.write(str(inference_instance))
    except Exception as e:
        print(f"추론 중 오류 발생: {e}")

@app.get("/refresh_weather", response_class=HTMLResponse)
async def refresh_weather(request: Request):
    location = get_location_by_ip()
    weather_info = get_naver_weather(location)
    
    global global_context
    global_context.update({
        "location": weather_info['location'],
        "temperature": weather_info['temperature'],
        "wether": weather_info['weather']
    })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        **global_context
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)