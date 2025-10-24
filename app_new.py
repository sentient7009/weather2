import streamlit as st
import requests
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="🌤️ 날씨 정보 앱",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OpenWeather API 설정 (환경변수에서 로드)
API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def check_api_key_configuration():
    """API 키가 제대로 설정되었는지 확인합니다."""
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        return False
    return True

def display_api_key_setup_guide():
    """API 키 설정 가이드를 표시합니다."""
    st.error("🔑 **API 키가 설정되어 있지 않습니다!**")
    st.markdown("---")
    
    st.subheader("🔧 Streamlit Cloud에서 환경변수 설정하기")
    
    st.markdown("""
    **1단계: Streamlit Cloud 앱 설정으로 이동**
    - 배포된 앱 페이지에서 오른쪽 상단 "⚙️ Settings" 클릭
    
    **2단계: Secrets 섹션 찾기**
    - 왼쪽 메뉴에서 "🔐 Secrets" 클릭
    
    **3단계: 환경변수 추가**
    - 다음 내용을 입력창에 복사해서 붙여넣기:
    ```
    OPENWEATHER_API_KEY = "your_actual_api_key_here"
    ```
    
    **4단계: API 키 발급받기**
    """)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        1. [OpenWeather 회원가입](https://openweathermap.org/api) 하기
        2. 이메일 인증 완료
        3. "API Keys" 메뉴로 이동
        4. 기본 API 키 복사하기
        """)
    
    with col2:
        st.info("""
        💡 **무료 계정 제한**
        - 1,000회/일 호출 제한
        - 새 API 키는 2시간 후 활성화
        """)
    
    st.markdown("""
    **5단계: 설정 완료**
    - API 키를 복사해서 위의 `your_actual_api_key_here` 부분에 붙여넣기
    - "Save" 버튼 클릭
    - 앱이 자동으로 재시작됩니다
    """)
    
    st.markdown("---")
    st.subheader("🏠 로컬 개발 환경")
    st.markdown("""
    로컬에서 개발할 때는 프로젝트 폴더에 `.env` 파일을 만들고:
    ```
    OPENWEATHER_API_KEY=your_actual_api_key_here
    ```
    """)
    
    st.warning("⚠️ API 키를 설정한 후 앱을 새로고침해주세요!")
    
    return False

# 세션 상태 초기화
if 'api_status' not in st.session_state:
    st.session_state.api_status = 'unknown'
if 'last_api_check' not in st.session_state:
    st.session_state.last_api_check = 0

# 한글 도시명 매핑
KOREAN_CITY_MAPPING = {
    # 광역시/특별시
    "서울": "Seoul", "서울시": "Seoul", "서울특별시": "Seoul",
    "부산": "Busan", "부산시": "Busan", "부산광역시": "Busan",
    "대구": "Daegu", "대구시": "Daegu", "대구광역시": "Daegu",
    "인천": "Incheon", "인천시": "Incheon", "인천광역시": "Incheon",
    "광주": "Gwangju", "광주시": "Gwangju", "광주광역시": "Gwangju",
    "대전": "Daejeon", "대전시": "Daejeon", "대전광역시": "Daejeon",
    "울산": "Ulsan", "울산시": "Ulsan", "울산광역시": "Ulsan",
    
    # 도청소재지 및 주요 도시
    "수원": "Suwon", "수원시": "Suwon",
    "춘천": "Chuncheon", "춘천시": "Chuncheon",
    "청주": "Cheongju", "청주시": "Cheongju",
    "전주": "Jeonju", "전주시": "Jeonju",
    "포항": "Pohang", "포항시": "Pohang",
    "창원": "Changwon", "창원시": "Changwon",
    "제주": "Jeju", "제주시": "Jeju", "제주도": "Jeju",
    
    # 도 단위
    "경기도": "Suwon", "강원도": "Chuncheon", 
    "충청북도": "Cheongju", "충청남도": "Daejeon",
    "충북": "Cheongju", "충남": "Daejeon",
    "전라북도": "Jeonju", "전라남도": "Gwangju",
    "전북": "Jeonju", "전남": "Gwangju",
    "경상북도": "Daegu", "경상남도": "Changwon",
    "경북": "Daegu", "경남": "Changwon",
    
    # 기타 주요 도시
    "안양": "Anyang", "안산": "Ansan", "고양": "Goyang",
    "성남": "Seongnam", "용인": "Yongin", "부천": "Bucheon",
    "천안": "Cheonan", "마산": "Masan", "진주": "Jinju",
    "목포": "Mokpo", "여수": "Yeosu", "순천": "Suncheon"
}

def check_api_key_status():
    """API 키 상태를 확인합니다."""
    current_time = time.time()
    
    # 5분마다 API 상태 체크 (캐싱)
    if current_time - st.session_state.last_api_check < 300:
        return st.session_state.api_status
    
    try:
        test_params = {
            'q': 'London',
            'appid': API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(BASE_URL, params=test_params, timeout=10)
        
        if response.status_code == 200:
            st.session_state.api_status = 'active'
        elif response.status_code == 401:
            st.session_state.api_status = 'invalid'
        else:
            st.session_state.api_status = 'error'
            
    except requests.exceptions.RequestException:
        st.session_state.api_status = 'network_error'
    
    st.session_state.last_api_check = current_time
    return st.session_state.api_status

def convert_korean_to_english_city(city_name):
    """한글 도시명을 영어로 변환"""
    city_name = city_name.strip()
    
    if city_name in KOREAN_CITY_MAPPING:
        return KOREAN_CITY_MAPPING[city_name], True
    
    return city_name, False

def get_demo_weather_data(city_name):
    """데모 날씨 데이터"""
    demo_data = {
        "seoul": {
            "name": "Seoul", "sys": {"country": "KR", "sunrise": 1698106800, "sunset": 1698145200},
            "main": {"temp": 18.5, "feels_like": 17.2, "humidity": 65, "pressure": 1013, "temp_min": 15.0, "temp_max": 22.0},
            "weather": [{"description": "구름조금", "icon": "02d"}], "wind": {"speed": 2.5}, "cod": 200
        },
        "busan": {
            "name": "Busan", "sys": {"country": "KR", "sunrise": 1698106900, "sunset": 1698145300},
            "main": {"temp": 20.1, "feels_like": 19.8, "humidity": 72, "pressure": 1015, "temp_min": 17.0, "temp_max": 23.0},
            "weather": [{"description": "맑음", "icon": "01d"}], "wind": {"speed": 3.1}, "cod": 200
        },
        "incheon": {
            "name": "Incheon", "sys": {"country": "KR", "sunrise": 1698106750, "sunset": 1698145150},
            "main": {"temp": 17.8, "feels_like": 16.9, "humidity": 68, "pressure": 1012, "temp_min": 14.0, "temp_max": 21.0},
            "weather": [{"description": "흐림", "icon": "04d"}], "wind": {"speed": 2.8}, "cod": 200
        },
        "daegu": {
            "name": "Daegu", "sys": {"country": "KR", "sunrise": 1698107000, "sunset": 1698145400},
            "main": {"temp": 19.3, "feels_like": 18.7, "humidity": 61, "pressure": 1016, "temp_min": 16.0, "temp_max": 22.0},
            "weather": [{"description": "맑음", "icon": "01d"}], "wind": {"speed": 2.2}, "cod": 200
        },
        "daejeon": {
            "name": "Daejeon", "sys": {"country": "KR", "sunrise": 1698106850, "sunset": 1698145250},
            "main": {"temp": 18.7, "feels_like": 17.9, "humidity": 64, "pressure": 1014, "temp_min": 15.0, "temp_max": 21.0},
            "weather": [{"description": "구름조금", "icon": "02d"}], "wind": {"speed": 2.1}, "cod": 200
        },
        "gwangju": {
            "name": "Gwangju", "sys": {"country": "KR", "sunrise": 1698107100, "sunset": 1698145500},
            "main": {"temp": 20.5, "feels_like": 19.8, "humidity": 70, "pressure": 1013, "temp_min": 17.0, "temp_max": 23.0},
            "weather": [{"description": "맑음", "icon": "01d"}], "wind": {"speed": 2.9}, "cod": 200
        },
        "ulsan": {
            "name": "Ulsan", "sys": {"country": "KR", "sunrise": 1698107050, "sunset": 1698145450},
            "main": {"temp": 19.8, "feels_like": 19.2, "humidity": 69, "pressure": 1015, "temp_min": 16.0, "temp_max": 22.0},
            "weather": [{"description": "구름많음", "icon": "03d"}], "wind": {"speed": 3.3}, "cod": 200
        },
        "suwon": {
            "name": "Suwon", "sys": {"country": "KR", "sunrise": 1698106780, "sunset": 1698145180},
            "main": {"temp": 18.2, "feels_like": 17.5, "humidity": 66, "pressure": 1013, "temp_min": 15.0, "temp_max": 21.0},
            "weather": [{"description": "구름조금", "icon": "02d"}], "wind": {"speed": 2.4}, "cod": 200
        },
        "chuncheon": {
            "name": "Chuncheon", "sys": {"country": "KR", "sunrise": 1698106700, "sunset": 1698145100},
            "main": {"temp": 16.1, "feels_like": 15.3, "humidity": 71, "pressure": 1011, "temp_min": 12.0, "temp_max": 19.0},
            "weather": [{"description": "안개", "icon": "50d"}], "wind": {"speed": 1.8}, "cod": 200
        },
        "cheongju": {
            "name": "Cheongju", "sys": {"country": "KR", "sunrise": 1698106820, "sunset": 1698145220},
            "main": {"temp": 17.9, "feels_like": 17.1, "humidity": 67, "pressure": 1012, "temp_min": 14.0, "temp_max": 20.0},
            "weather": [{"description": "구름많음", "icon": "03d"}], "wind": {"speed": 2.3}, "cod": 200
        },
        "jeonju": {
            "name": "Jeonju", "sys": {"country": "KR", "sunrise": 1698107050, "sunset": 1698145450},
            "main": {"temp": 19.4, "feels_like": 18.8, "humidity": 68, "pressure": 1014, "temp_min": 16.0, "temp_max": 22.0},
            "weather": [{"description": "맑음", "icon": "01d"}], "wind": {"speed": 2.6}, "cod": 200
        },
        "jeju": {
            "name": "Jeju", "sys": {"country": "KR", "sunrise": 1698107200, "sunset": 1698145600},
            "main": {"temp": 22.3, "feels_like": 21.9, "humidity": 75, "pressure": 1016, "temp_min": 19.0, "temp_max": 25.0},
            "weather": [{"description": "구름조금", "icon": "02d"}], "wind": {"speed": 4.1}, "cod": 200
        },
        "tokyo": {
            "name": "Tokyo", "sys": {"country": "JP", "sunrise": 1698106200, "sunset": 1698144600},
            "main": {"temp": 21.3, "feels_like": 20.8, "humidity": 58, "pressure": 1018, "temp_min": 18.0, "temp_max": 24.0},
            "weather": [{"description": "맑음", "icon": "01d"}], "wind": {"speed": 1.8}, "cod": 200
        },
        "new york": {
            "name": "New York", "sys": {"country": "US", "sunrise": 1698142800, "sunset": 1698180000},
            "main": {"temp": 16.2, "feels_like": 15.1, "humidity": 72, "pressure": 1010, "temp_min": 12.0, "temp_max": 19.0},
            "weather": [{"description": "흐림", "icon": "04d"}], "wind": {"speed": 3.2}, "cod": 200
        },
        "london": {
            "name": "London", "sys": {"country": "GB", "sunrise": 1698142200, "sunset": 1698179400},
            "main": {"temp": 12.8, "feels_like": 11.5, "humidity": 78, "pressure": 1008, "temp_min": 9.0, "temp_max": 15.0},
            "weather": [{"description": "비", "icon": "10d"}], "wind": {"speed": 4.2}, "cod": 200
        },
        "paris": {
            "name": "Paris", "sys": {"country": "FR", "sunrise": 1698142500, "sunset": 1698179700},
            "main": {"temp": 14.6, "feels_like": 13.9, "humidity": 68, "pressure": 1012, "temp_min": 11.0, "temp_max": 17.0},
            "weather": [{"description": "구름많음", "icon": "03d"}], "wind": {"speed": 2.8}, "cod": 200
        }
    }
    
    return demo_data.get(city_name.lower(), None)

def get_weather_data(city_name):
    """날씨 데이터를 가져옵니다 - API 또는 데모 모드"""
    
    # 한글 도시명 변환
    english_city, was_converted = convert_korean_to_english_city(city_name)
    
    if was_converted:
        st.info(f"🔄 '{city_name}' → '{english_city}'로 변환하여 검색합니다.")
    
    # API 상태 확인
    api_status = check_api_key_status()
    
    # API가 활성화된 경우 실제 API 호출 시도
    if api_status == 'active':
        try:
            params = {
                'q': english_city,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'kr'
            }
            
            with st.spinner('🌐 실시간 날씨 데이터를 가져오는 중...'):
                response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ 실시간 날씨 데이터를 성공적으로 가져왔습니다!")
                return data
            elif response.status_code == 404:
                st.error(f"🏙️ '{city_name}' 도시를 찾을 수 없습니다.")
                return None
            else:
                st.warning("⚠️ API 오류 발생. 데모 모드로 전환합니다.")
                
        except requests.exceptions.Timeout:
            st.warning("⏱️ 요청 시간 초과. 데모 모드로 전환합니다.")
        except requests.exceptions.RequestException as e:
            st.warning(f"🌐 네트워크 오류. 데모 모드로 전환합니다: {str(e)}")
    
    # 데모 모드 실행
    demo_data = get_demo_weather_data(english_city)
    if demo_data:
        if api_status == 'invalid':
            st.warning("🔑 API 키가 유효하지 않습니다. 데모 모드로 실행됩니다.")
        elif api_status == 'network_error':
            st.warning("🌐 네트워크 연결 문제. 데모 모드로 실행됩니다.")
        
        st.info("✨ 데모 데이터를 사용하여 날씨 정보를 표시합니다.")
        return demo_data
    else:
        available_cities = "서울, 부산, 인천, 대구, 대전, 광주, 울산, 수원, 춘천, 청주, 전주, 제주, Tokyo, New York, London, Paris"
        st.error(f"😔 '{city_name}'에 대한 데이터가 없습니다.")
        st.info(f"🏙️ **사용 가능한 도시**: {available_cities}")
        return None

def display_weather_info(weather_data):
    """날씨 정보를 화면에 표시합니다"""
    if not weather_data:
        return
    
    # 기본 정보 추출
    city_name = weather_data['name']
    country = weather_data['sys']['country']
    temperature = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    description = weather_data['weather'][0]['description']
    icon = weather_data['weather'][0]['icon']
    wind_speed = weather_data['wind']['speed']
    
    # 헤더
    st.header(f"🌍 {city_name}, {country}")
    
    # 메인 정보 (3개 컬럼)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌡️ 현재 온도",
            value=f"{temperature:.1f}°C",
            delta=f"체감 {feels_like:.1f}°C"
        )
    
    with col2:
        st.metric(
            label="💧 습도",
            value=f"{humidity}%"
        )
    
    with col3:
        st.metric(
            label="🌪️ 풍속",
            value=f"{wind_speed} m/s"
        )
    
    # 날씨 상태
    st.subheader("☁️ 날씨 상태")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        st.image(icon_url, width=100)
    with col2:
        st.write(f"**{description.title()}**")
        st.write(f"**기압:** {pressure} hPa")
    
    # 추가 정보
    if 'temp_min' in weather_data['main'] and 'temp_max' in weather_data['main']:
        temp_min = weather_data['main']['temp_min']
        temp_max = weather_data['main']['temp_max']
        
        st.subheader("📊 상세 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🔽 **최저 온도:** {temp_min:.1f}°C")
        with col2:
            st.write(f"🔼 **최고 온도:** {temp_max:.1f}°C")
    
    # 일출/일몰
    if 'sunrise' in weather_data['sys'] and 'sunset' in weather_data['sys']:
        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🌅 **일출:** {sunrise}")
        with col2:
            st.write(f"🌇 **일몰:** {sunset}")

def main():
    """메인 애플리케이션"""
    
    # API 키 설정 확인
    if not check_api_key_configuration():
        display_api_key_setup_guide()
        return
    
    # 제목
    st.title("🌤️ 실시간 날씨 정보")
    st.markdown("---")
    
    # API 상태 표시
    api_status = check_api_key_status()
    
    if api_status == 'active':
        st.success("🟢 **API 상태**: 정상 작동 중 - 실시간 데이터 제공")
    elif api_status == 'invalid':
        st.error("🔴 **API 상태**: API 키 유효하지 않음 - 데모 모드 실행")
    elif api_status == 'network_error':
        st.warning("🟡 **API 상태**: 네트워크 오류 - 데모 모드 실행")
    else:
        st.info("🔵 **API 상태**: 확인 중...")
    
    # 사이드바
    with st.sidebar:
        st.title("📱 사용법")
        st.markdown("""
        1. 도시명을 **한글** 또는 **영어**로 입력
        2. '날씨 조회' 버튼 클릭
        3. 실시간 날씨 정보 확인!
        
        **한글 입력 예시:**
        - 서울, 부산, 인천, 대구, 대전
        - 광주, 울산, 수원, 춘천, 청주
        - 전주, 제주, 강원도, 경기도
        
        **영어 입력 예시:**
        - Seoul, Busan, Tokyo, New York
        """)
        
        st.markdown("---")
        st.title("🔑 API 설정")
        
        if api_status == 'active':
            st.success("✅ API 키가 정상적으로 작동 중입니다!")
        else:
            st.markdown("""
            **새 API 키 발급:**
            1. [OpenWeather 회원가입](https://openweathermap.org/api)
            2. API Keys에서 새 키 생성
            3. 코드에서 API_KEY 값 변경
            4. 앱 재시작
            
            ⚠️ 새 API 키는 활성화까지 최대 2시간 소요
            """)
        
        st.markdown("---")
        st.markdown(f"**데모 지원 도시:** 16개")
        st.markdown("🇰🇷 한국 12개 도시")
        st.markdown("🌍 해외 4개 도시")
    

    
    # 한국 도시 버튼들
    st.subheader("🇰🇷 한국 주요 도시")
    korean_cities = ["서울", "부산", "인천", "대구", "대전", "광주", "울산", "수원", "춘천", "청주", "전주", "제주"]
    
    cols = st.columns(4)
    for i, city in enumerate(korean_cities):
        with cols[i % 4]:
            if st.button(f"📍 {city}", key=f"kr_{city}"):
                # 날씨 데이터 바로 표시
                weather_data = get_weather_data(city)
                if weather_data:
                    st.markdown("---")
                    display_weather_info(weather_data)
    
    # 해외 도시 버튼들
    st.subheader("🌍 해외 주요 도시")
    international_cities = ["Tokyo", "New York", "London", "Paris"]
    
    cols = st.columns(len(international_cities))
    for i, city in enumerate(international_cities):
        with cols[i]:
            if st.button(f"🌏 {city}", key=f"intl_{city}"):
                # 날씨 데이터 바로 표시
                weather_data = get_weather_data(city)
                if weather_data:
                    st.markdown("---")
                    display_weather_info(weather_data)
    

    
    # 푸터
    st.markdown("---")
    st.markdown("📊 **데이터 제공:** OpenWeatherMap API")
    st.markdown("🔄 **마지막 업데이트:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()