import requests
import json

def get_ip_info():
    """
    현재 공개 IP 주소와 해당 위치 정보를 가져옵니다.
    """
    try:
        ip_response = requests.get('https://ipapi.co/json/')
        ip_data = ip_response.json()
        
        return {
            'ip': ip_data.get('ip'),
            'city': ip_data.get('city'),
            'region': ip_data.get('region'),
            'country': ip_data.get('country_name'),
            'latitude': ip_data.get('latitude'),
            'longitude': ip_data.get('longitude')
        }
    except Exception as e:
        print(f"IP 정보를 가져오는 중 오류 발생: {e}")
        return None

def get_weather_info(lat, lon):
    """
    OpenWeatherMap API를 사용하여 날씨 정보를 가져옵니다.
    """
    API_KEY = "8e14464ae8812105e4f106aee4182812"  # 여기에 실제 API 키 입력
    
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

def main():
    # IP 정보 가져오기
    ip_info = get_ip_info()
    
    if ip_info:
        print("🌐 IP 정보:")
        print(f"IP 주소: {ip_info['ip']}")
        print(f"도시: {ip_info['city']}")
        print(f"지역: {ip_info['region']}")
        print(f"국가: {ip_info['country']}")
        
        # 날씨 정보 가져오기
        weather_info = get_weather_info(ip_info['latitude'], ip_info['longitude'])
        
        if weather_info:
            print("\n🌦️ 현재 날씨:")
            print(f"기온: {weather_info['temperature']}°C")
            print(f"체감 온도: {weather_info['feels_like']}°C")
            print(f"습도: {weather_info['humidity']}%")
            print(f"날씨 상태: {weather_info['description']}")

if __name__ == "__main__":
    main()