import streamlit as st
import requests
import json
import time
import os
import random
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Weather Info App",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 블랙앤옐로우 테마 CSS 적용
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a00 50%, #2d2d00 100%);
        color: #ffffff;
    }
    
    /* 사이드바 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a00 0%, #2d2d00 100%);
    }
    
    /* 헤더 스타일 */
    .css-10trblm {
        color: #ffeb3b;
        font-weight: 600;
    }
    
    /* 메트릭 박스 */
    .css-1r6slb0 {
        background: rgba(255, 235, 59, 0.1);
        border: 1px solid #ffd600;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(45deg, #f57f17, #ffeb3b);
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        height: 50px;
        min-height: 50px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff8f00, #ffd600);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(255, 214, 0, 0.4);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input {
        background: rgba(255, 235, 59, 0.1);
        border: 1px solid #ffd600;
        color: white;
        border-radius: 8px;
    }
    
    /* 정보 박스 */
    .stInfo {
        background: rgba(255, 235, 59, 0.3) !important;
        border-left: 4px solid #ffeb3b !important;
        color: #000000 !important;
    }
    
    /* 성공 박스 */
    .stSuccess {
        background: rgba(139, 195, 74, 0.1);
        border-left: 4px solid #8bc34a;
    }
    
    /* 경고 박스 */
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
    }
    
    /* 에러 박스 */
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
    }
    
    /* 날씨 컨테이너 */
    .weather-container {
        background: linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(255, 214, 0, 0.2) 100%);
        border: 1px solid #ffd600;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(66, 165, 245, 0.2);
    }
    
    /* 추가 정보 박스 스타일 오버라이드 */
    .stAlert > div[data-baseweb="notification"] {
        background: rgba(255, 235, 59, 0.3) !important;
        border-left: 4px solid #ffeb3b !important;
        color: #000000 !important;
    }
    
    .stAlert[data-baseweb="notification"] {
        background: rgba(255, 235, 59, 0.3) !important;
        border-left: 4px solid #ffeb3b !important;
        color: #000000 !important;
    }
    
    /* Streamlit info 요소들 */
    .element-container .stAlert .stMarkdown {
        color: #000000 !important;
    }
    
    /* 텍스트 색상 */
    .css-1v0mbdj {
        color: #e3f2fd;
    }
    
    /* 한국 주요 도시 헤더만 숨기기 */
    h3:contains("한국 주요 도시") {
        color: transparent !important;
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 일반 헤더들은 검정색으로 유지 */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #000000 !important;
    }
    
    /* 메인 제목들 검정색으로 복원 */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: #000000 !important;
    }
    
    /* 특정 헤더만 숨기기 (더 구체적으로) */
    .stMarkdown h3:contains("한국 주요 도시") {
        display: none !important;
    }
    
    /* AI 질문 예시 버튼들 크기 조정 */
    div[data-testid="column"]:has(button:contains("빨래")) .stButton > button,
    div[data-testid="column"]:has(button:contains("소풍")) .stButton > button,
    div[data-testid="column"]:has(button:contains("옷")) .stButton > button,
    div[data-testid="column"]:has(button:contains("운동")) .stButton > button {
        height: 65px !important;
        min-height: 65px !important;
        font-size: 18px !important;
        padding: 15px 10px !important;
        line-height: 1.2 !important;
    }
</style>
""", unsafe_allow_html=True)

# OpenWeather API 설정
# 환경변수에서 API 키를 가져오고, 없으면 기본값 사용 (개발용)
API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")  # .env 파일에서 API 키 로드
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  # 5일 예보 API

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
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None
if 'show_forecast' not in st.session_state:
    st.session_state.show_forecast = {}
if 'show_map' not in st.session_state:
    st.session_state.show_map = False
if 'diary_saved' not in st.session_state:
    st.session_state.diary_saved = False

# 한국 도시 좌표 데이터
KOREAN_CITIES_COORDINATES = {
    "서울": {"lat": 37.5665, "lon": 126.9780, "eng": "Seoul"},
    "부산": {"lat": 35.1796, "lon": 129.0756, "eng": "Busan"},
    "인천": {"lat": 37.4563, "lon": 126.7052, "eng": "Incheon"},
    "대구": {"lat": 35.8714, "lon": 128.6014, "eng": "Daegu"},
    "대전": {"lat": 36.3504, "lon": 127.3845, "eng": "Daejeon"},
    "광주": {"lat": 35.1595, "lon": 126.8526, "eng": "Gwangju"},
    "울산": {"lat": 35.5384, "lon": 129.3114, "eng": "Ulsan"},
    "수원": {"lat": 37.2636, "lon": 127.0286, "eng": "Suwon"},
    "춘천": {"lat": 37.8813, "lon": 127.7298, "eng": "Chuncheon"},
    "청주": {"lat": 36.6424, "lon": 127.4890, "eng": "Cheongju"},
    "전주": {"lat": 35.8242, "lon": 127.1480, "eng": "Jeonju"},
    "제주": {"lat": 33.4996, "lon": 126.5312, "eng": "Jeju"},
    "김포": {"lat": 37.6158, "lon": 126.7159, "eng": "Kimpo"}
}

# 한글 도시명을 영어로 변환하는 매핑
KOREAN_CITY_MAPPING = {
    # 광역시/특별시
    "서울": "Seoul",
    "서울시": "Seoul", 
    "서울특별시": "Seoul",
    "부산": "Busan",
    "부산시": "Busan",
    "부산광역시": "Busan",
    "대구": "Daegu",
    "대구시": "Daegu", 
    "대구광역시": "Daegu",
    "인천": "Incheon",
    "인천시": "Incheon",
    "인천광역시": "Incheon",
    "광주": "Gwangju",
    "광주시": "Gwangju",
    "광주광역시": "Gwangju",
    "대전": "Daejeon", 
    "대전시": "Daejeon",
    "대전광역시": "Daejeon",
    "울산": "Ulsan",
    "울산시": "Ulsan",
    "울산광역시": "Ulsan",
    
    # 도청소재지 및 주요 도시
    "수원": "Suwon",
    "수원시": "Suwon",
    "춘천": "Chuncheon", 
    "춘천시": "Chuncheon",
    "청주": "Cheongju",
    "청주시": "Cheongju", 
    "전주": "Jeonju",
    "전주시": "Jeonju",
    "포항": "Pohang",
    "포항시": "Pohang",
    "창원": "Changwon",
    "창원시": "Changwon",
    "제주": "Jeju",
    "제주시": "Jeju",
    "제주도": "Jeju",
    
    # 도 단위 (주요 도시로 매핑)
    "경기도": "Suwon",
    "강원도": "Chuncheon", 
    "충청북도": "Cheongju",
    "충청남도": "Daejeon",
    "충북": "Cheongju",
    "충남": "Daejeon",
    "전라북도": "Jeonju",
    "전라남도": "Gwangju", 
    "전북": "Jeonju",
    "전남": "Gwangju",
    "경상북도": "Daegu",
    "경상남도": "Changwon",
    "경북": "Daegu", 
    "경남": "Changwon",
    
    # 기타 주요 도시
    "안양": "Anyang",
    "안산": "Ansan", 
    "고양": "Goyang",
    "성남": "Seongnam",
    "용인": "Yongin",
    "부천": "Bucheon",
    "김포": "Incheon",
    "김포시": "Incheon",
    "천안": "Cheonan",
    "전주": "Jeonju",
    "마산": "Masan",
    "진주": "Jinju",
    "목포": "Mokpo",
    "여수": "Yeosu",
    "순천": "Suncheon"
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

def get_temperature_color(temp):
    """온도에 따른 색상을 반환합니다"""
    if temp < 0:
        return '#0000FF'  # 파란색 (매우 추움)
    elif temp < 10:
        return '#4169E1'  # 로얄 블루 (추움)
    elif temp < 20:
        return '#32CD32'  # 라임 그린 (선선함)
    elif temp < 25:
        return '#FFD700'  # 골드 (적당함)
    elif temp < 30:
        return '#FF8C00'  # 다크 오렌지 (더움)
    else:
        return '#FF0000'  # 빨간색 (매우 더움)

def get_weather_icon_emoji(icon_code):
    """OpenWeather 아이콘 코드를 텍스트로 변환"""
    icon_map = {
        '01d': 'SUN', '01n': 'MOON',  # 맑음
        '02d': 'PARTLY_CLOUDY', '02n': 'CLOUDY',  # 구름조금
        '03d': 'CLOUDY', '03n': 'CLOUDY',  # 구름많음
        '04d': 'CLOUDY', '04n': 'CLOUDY',  # 흐림
        '09d': 'RAIN', '09n': 'RAIN',  # 소나기
        '10d': 'RAIN', '10n': 'RAIN',  # 비
        '11d': 'STORM', '11n': 'STORM',  # 천둥번개
        '13d': 'SNOW', '13n': 'SNOW',  # 눈
        '50d': 'FOG', '50n': 'FOG'   # 안개
    }
    return icon_map.get(icon_code, 'CLEAR')

def create_korea_weather_map(center_city=None):
    """한국 전국 날씨 지도를 생성합니다"""
    # 중심 좌표 설정
    if center_city and center_city in KOREAN_CITIES_COORDINATES:
        center_coords = KOREAN_CITIES_COORDINATES[center_city]
        center_lat, center_lon = center_coords["lat"], center_coords["lon"]
        zoom_level = 10  # 도시 선택시 더 가까이
    else:
        center_lat, center_lon = 36.5, 127.5  # 한국 중심
        zoom_level = 7
    
    # 지도 생성
    korea_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )
    
    # 각 도시의 날씨 정보를 지도에 추가
    for city_name, coordinates in KOREAN_CITIES_COORDINATES.items():
        try:
            # 날씨 데이터 가져오기 (데모 데이터 사용)
            weather_data = get_demo_weather_data(coordinates["eng"].lower())
            
            if weather_data:
                temp = weather_data['main']['temp']
                desc = weather_data['weather'][0].get('description', 
                      weather_data['weather'][0].get('desc', ''))
                icon = weather_data['weather'][0]['icon']
                humidity = weather_data['main']['humidity']
                
                # 온도에 따른 색상
                color = get_temperature_color(temp)
                
                # 날씨 아이콘 이모지
                weather_emoji = get_weather_icon_emoji(icon)
                
                # 선택된 도시인지 확인
                is_selected = (center_city == city_name)
                marker_radius = 20 if is_selected else 15
                marker_weight = 4 if is_selected else 2
                
                # 마커 생성
                folium.CircleMarker(
                    location=[coordinates["lat"], coordinates["lon"]],
                    radius=marker_radius,
                    popup=folium.Popup(f"""
                    <div style="width: 200px; text-align: center;">
                        <h4>{weather_emoji} {city_name}</h4>
                        <p><strong>{temp}°C</strong></p>
                        <p>{desc}</p>
                        <p>습도: {humidity}%</p>
                        {'<p><strong>선택된 도시</strong></p>' if is_selected else ''}
                    </div>
                    """, max_width=300),
                    tooltip=f"{city_name}: {temp}°C",
                    color='#FFD700' if is_selected else 'white',
                    fillColor=color,
                    fillOpacity=0.9 if is_selected else 0.8,
                    weight=marker_weight
                ).add_to(korea_map)
                
                # 온도 텍스트 오버레이
                folium.Marker(
                    location=[coordinates["lat"], coordinates["lon"]],
                    icon=folium.DivIcon(
                        html=f'<div style="color: white; font-weight: bold; font-size: 12px; text-shadow: 1px 1px 1px black;">{temp}°C</div>',
                        icon_size=(50, 20),
                        icon_anchor=(25, 10)
                    )
                ).add_to(korea_map)
        
        except Exception as e:
            print(f"Error processing {city_name}: {e}")
    
    # 범례 추가
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>온도 범례</h4>
    <p><span style="color:#0000FF;">●</span> 0°C 미만 (매우 추움)</p>
    <p><span style="color:#4169E1;">●</span> 0-10°C (추움)</p>
    <p><span style="color:#32CD32;">●</span> 10-20°C (선선함)</p>
    <p><span style="color:#FFD700;">●</span> 20-25°C (적당함)</p>
    <p><span style="color:#FF8C00;">●</span> 25-30°C (더움)</p>
    <p><span style="color:#FF0000;">●</span> 30°C 이상 (매우 더움)</p>
    </div>
    '''
    korea_map.get_root().html.add_child(folium.Element(legend_html))
    
    return korea_map

def save_weather_diary(city, weather_data, diary_text, mood):
    """날씨 일기를 저장합니다"""
    import os
    from datetime import datetime
    
    # 일기 저장 디렉토리 생성
    diary_dir = "weather_diary"
    if not os.path.exists(diary_dir):
        os.makedirs(diary_dir)
    
    # 오늘 날짜로 파일명 생성
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{diary_dir}/diary_{today}.txt"
    
    # 날씨 정보 추출
    temp = weather_data['main']['temp']
    desc = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    humidity = weather_data['main']['humidity']
    
    # 일기 내용 구성
    diary_entry = f"""
=== 날씨 일기 | {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")} ===
도시: {city}
온도: {temp}°C
날씨: {desc}
습도: {humidity}%
기분: {mood}

오늘의 일기:
{diary_text}

{'='*50}

"""
    
    # 파일에 추가 저장 (하루에 여러 번 쓸 수 있도록)
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(diary_entry)
        return True, filename
    except Exception as e:
        return False, str(e)

def load_weather_diaries():
    """저장된 날씨 일기들을 불러옵니다"""
    import os
    import glob
    
    diary_dir = "weather_diary"
    if not os.path.exists(diary_dir):
        return []
    
    # 모든 일기 파일 찾기
    diary_files = glob.glob(f"{diary_dir}/diary_*.txt")
    diaries = []
    
    for file_path in sorted(diary_files, reverse=True):  # 최신 순
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 파일명에서 날짜 추출
                filename = os.path.basename(file_path)
                date = filename.replace('diary_', '').replace('.txt', '')
                diaries.append({
                    'date': date,
                    'content': content,
                    'file_path': file_path
                })
        except Exception as e:
            continue
    
    return diaries

def get_weather_mood_suggestions(weather_data):
    """날씨에 따른 기분 제안"""
    if not weather_data:
        return ["😊 좋음", "😐 보통", "😔 별로"]
    
    temp = weather_data['main']['temp']
    desc = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    
    if "맑" in desc or "clear" in desc.lower():
        return ["😊 상쾌함", "🌞 기분좋음", "✨ 활기참", "😊 좋음"]
    elif "비" in desc or "rain" in desc.lower():
        return ["🌧️ 차분함", "💭 사색적", "😌 평온함", "😐 보통"]
    elif "구름" in desc:
        return ["☁️ 편안함", "😌 평온함", "💭 생각많음", "😊 좋음"]
    elif temp > 25:
        return ["🌞 활발함", "💦 더위먹음", "😅 땀남", "😊 좋음"]
    elif temp < 10:
        return ["🧊 추움", "☃️ 겨울느낌", "😌 포근함", "😊 좋음"]
    else:
        return ["😊 좋음", "😌 평온함", "💭 생각많음", "😐 보통"]

def weather_ai_assistant(question, weather_data, forecast_data=None):
    """AI 스타일 날씨 개인 비서"""
    if not weather_data:
        return "😔 죄송해요, 날씨 정보를 먼저 조회해주세요!"
    
    question = question.lower().strip()
    temp = weather_data['main']['temp']
    desc = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    city = weather_data['name']
    
    # 질문 패턴 분석 및 응답
    responses = []
    
    # 소풍/나들이 관련
    if any(word in question for word in ['소풍', '나들이', '놀러', '여행', '데이트', '산책', '외출']):
        if temp >= 18 and temp <= 28 and "맑" in desc:
            responses.append(f"🎯 **완벽해요!** {city}는 {temp}°C로 {desc} 날씨예요! 소풍가기 최고의 날이에요! ☀️")
        elif temp >= 15 and temp <= 30 and "비" not in desc:
            responses.append(f"😊 **좋아요!** {city}는 {temp}°C예요. {desc} 날씨지만 나들이하기 괜찮아요!")
        elif "비" in desc:
            responses.append(f"☔ **아쉬워요...** {city}에 비가 와요. 실내 활동은 어떨까요?")
        else:
            responses.append(f"🤔 **글쎄요...** {city}는 {temp}°C로 {desc} 날씨예요. 옷을 따뜻하게 입고 가세요!")
    
    # 빨래 관련
    elif any(word in question for word in ['빨래', '세탁', '말리기', '건조']):
        if humidity < 60 and "비" not in desc and wind_speed > 1:
            responses.append(f"👍 **네! 완벽해요!** {city}는 습도 {humidity}%, 바람 {wind_speed}m/s로 빨래 말리기 최고예요! 🌬️")
        elif humidity < 70 and "비" not in desc:
            responses.append(f"✅ **괜찮아요!** {city}는 습도 {humidity}%로 빨래 말리기에 나쁘지 않아요!")
        elif "비" in desc:
            responses.append(f"❌ **안돼요!** {city}에 비가 와요. 실내에서 말리세요! ☔")
        else:
            responses.append(f"😐 **별로예요...** {city}는 습도 {humidity}%로 높아요. 실내 건조가 나을 것 같아요.")
    
    # 운동 관련
    elif any(word in question for word in ['운동', '조깅', '러닝', '산책', '자전거', '헬스']):
        if temp >= 15 and temp <= 25 and "비" not in desc:
            responses.append(f"💪 **완벽한 운동 날씨!** {city}는 {temp}°C로 운동하기 딱 좋아요! 🏃‍♂️")
        elif temp > 30:
            responses.append(f"🌡️ **너무 더워요!** {city}는 {temp}°C예요. 이른 아침이나 저녁에 운동하세요!")
        elif temp < 10:
            responses.append(f"🧥 **추워요!** {city}는 {temp}°C예요. 실내 운동이 좋겠어요!")
        elif "비" in desc:
            responses.append(f"☔ **비가 와서 아쉬워요!** {city}에 비가 와요. 실내 운동은 어떨까요?")
        else:
            responses.append(f"🤔 **적당해요!** {city}는 {temp}°C, {desc} 날씨예요. 가벼운 운동은 괜찮아요!")
    
    # 우산 관련
    elif any(word in question for word in ['우산', '비', 'rain', '비올']):
        if "비" in desc:
            responses.append(f"☂️ **네! 꼭 챙기세요!** {city}에 비가 와요. 우산 필수예요!")
        else:
            responses.append(f"☀️ **아니요!** {city}는 {desc} 날씨예요. 우산 없어도 괜찮아요!")
    
    # 옷차림 관련
    elif any(word in question for word in ['옷', '입을', '차림', '패션', '코디']):
        if temp < 5:
            responses.append(f"🧥 **두꺼운 패딩!** {city}는 {temp}°C로 매우 추워요. 목도리, 장갑도 필수!")
        elif temp < 10:
            responses.append(f"🧥 **따뜻한 외투!** {city}는 {temp}°C예요. 코트나 두꺼운 재킷 추천!")
        elif temp < 15:
            responses.append(f"👔 **가디건이나 자켓!** {city}는 {temp}°C로 선선해요. 얇은 겉옷 추천!")
        elif temp < 20:
            responses.append(f"👕 **긴팔 티셔츠!** {city}는 {temp}°C로 쾌적해요. 가벼운 옷 좋아요!")
        elif temp < 25:
            responses.append(f"👕 **반팔도 OK!** {city}는 {temp}°C로 따뜻해요. 편한 옷차림!")
        else:
            responses.append(f"🩳 **시원하게!** {city}는 {temp}°C로 더워요. 반팔, 반바지 추천!")
    
    # 드라이브 관련
    elif any(word in question for word in ['드라이브', '운전', '차']):
        if "안개" in desc:
            responses.append(f"🌫️ **주의하세요!** {city}에 안개가 있어요. 서행 운전 필수!")
        elif "비" in desc:
            responses.append(f"☔ **조심히 가세요!** {city}에 비가 와요. 미끄러운 도로 주의!")
        elif wind_speed > 7:
            responses.append(f"💨 **바람이 강해요!** {city}는 바람 {wind_speed}m/s예요. 핸들 꽉 잡으세요!")
        else:
            responses.append(f"🚗 **좋은 드라이브 날씨!** {city}는 {temp}°C, {desc} 날씨예요. 안전운전!")
    
    # 일반적인 날씨 질문
    elif any(word in question for word in ['날씨', '어때', '어떨까', '좋아', '괜찮']):
        if temp >= 20 and temp <= 25 and "맑" in desc:
            responses.append(f"**최고의 날씨!** {city}는 {temp}°C, {desc}로 완벽해요!")
        elif temp >= 15 and temp <= 28 and "비" not in desc:
            responses.append(f"😊 **좋은 날씨!** {city}는 {temp}°C, {desc}로 괜찮아요!")
        elif "비" in desc:
            responses.append(f"☔ **비 오는 날이에요!** {city}는 {temp}°C, {desc} 날씨예요.")
        else:
            responses.append(f"🌤️ **평범한 날씨!** {city}는 {temp}°C, {desc} 날씨예요.")
    
    # 이해하지 못한 질문
    else:
        responses.append(f"🤔 **음... 잘 이해 못했어요!** {city}는 현재 {temp}°C, {desc} 날씨예요. 더 구체적으로 질문해주세요!")
        responses.append("**이런 질문을 해보세요:**")
        responses.append("• '소풍 가도 될까요?'")
        responses.append("• '빨래 말리기 좋나요?'")
        responses.append("• '운동하기 어때요?'")
        responses.append("• '무슨 옷 입을까요?'")
    
    return responses

def get_weather_advice(weather_data):
    """날씨 데이터를 기반으로 실생활 조언을 제공합니다"""
    if not weather_data:
        return []
    
    temp = weather_data['main']['temp']
    desc = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    
    advice = []
    
    # 온도 기반 조언
    if temp < 5:
        advice.append("🧥 **두꺼운 외투 필수!** 매우 춥습니다.")
    elif temp < 10:
        advice.append("🧥 **따뜻한 외투를 챙기세요!** 쌀쌀합니다.")
    elif temp < 15:
        advice.append("👕 **얇은 겉옷이 좋겠어요.** 선선합니다.")
    elif temp < 20:
        advice.append("👔 **적당한 옷차림이 좋겠어요.** 쾌적한 날씨입니다.")
    elif temp < 25:
        advice.append("👕 **가벼운 옷이 편해요.** 따뜻한 날씨입니다.")
    elif temp < 30:
        advice.append("👕 **가벼운 옷차림을 추천!** 더워요.")
    else:
        advice.append("🌞 **시원한 옷차림을 추천!** 매우 덥습니다.")
    
    # 날씨 상태 기반 조언
    if "비" in desc or "rain" in desc.lower():
        advice.append("☂️ **우산을 꼭 챙기세요!** 비가 와요.")
    elif "눈" in desc or "snow" in desc.lower():
        advice.append("❄️ **미끄럼 주의!** 눈이 와요.")
    elif "맑" in desc or "clear" in desc.lower():
        advice.append("☀️ **야외활동하기 좋은 날이에요!** 맑아요.")
    elif "구름많음" in desc or "구름" in desc:
        advice.append("☁️ **구름이 많아요.** 선선한 느낌이에요.")
    elif "흐림" in desc or "cloudy" in desc.lower():
        advice.append("☁️ **흐린 날씨예요.** 실내 활동이 좋겠어요.")
    elif "안개" in desc or "fog" in desc.lower():
        advice.append("🌫️ **운전시 주의하세요.** 시야가 흐려요.")
    
    # 습도 기반 조언
    if humidity > 80:
        advice.append("💧 **습도가 높아요.** 불쾌할 수 있어요.")
    elif humidity < 30:
        advice.append("🏺 **습도가 낮아요.** 수분 보충 필요!")
    
    # 바람 기반 조언
    if wind_speed > 5:
        advice.append("💨 **바람이 강해요.** 우산보다 우비가 좋겠어요.")
    
    # 종합 조언
    if temp >= 20 and temp <= 25 and humidity < 70 and "맑" in desc:
        advice.append("🎯 **완벽한 날씨!** 나들이하기 최고예요!")
    
    # 기본 조언 (항상 하나는 보여주기)
    if len(advice) == 0:
        if temp >= 15 and temp <= 25:
            advice.append("😊 **쾌적한 날씨예요!** 좋은 하루 되세요!")
        else:
            advice.append("🌤️ **오늘도 안전한 하루 보내세요!**")
    
    return advice

def get_weather_background_color(weather_data):
    """날씨에 따른 블랙앤블루 테마 배경색을 반환합니다"""
    if not weather_data:
        return "rgba(25, 35, 126, 0.3)"  # 기본 네이비
    
    desc = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    temp = weather_data['main']['temp']
    
    if "맑" in desc or "clear" in desc.lower():
        return "rgba(33, 150, 243, 0.4)"  # 블루
    elif "구름" in desc or "cloud" in desc.lower():
        return "rgba(25, 35, 126, 0.5)"  # 다크 블루
    elif "비" in desc or "rain" in desc.lower():
        return "rgba(13, 27, 62, 0.7)"  # 딥 네이비
    elif "눈" in desc or "snow" in desc.lower():
        return "rgba(69, 90, 100, 0.5)"  # 블루 그레이
    elif "안개" in desc or "fog" in desc.lower():
        return "rgba(55, 71, 79, 0.6)"  # 그레이 블루
    elif temp > 30:
        return "rgba(25, 35, 126, 0.3)"  # 기본 네이비
    elif temp < 0:
        return "rgba(13, 27, 62, 0.8)"  # 콜드 네이비
    else:
        return "rgba(25, 35, 126, 0.4)"  # 기본색

def convert_korean_to_english_city(city_name):
    """
    한글 도시명을 영어로 변환
    """
    # 입력값 정리 (공백 제거)
    city_name = city_name.strip()
    
    # 한글 도시명이면 영어로 변환
    if city_name in KOREAN_CITY_MAPPING:
        english_name = KOREAN_CITY_MAPPING[city_name]
        return english_name, True  # 변환됨
    
    # 이미 영어이거나 매핑에 없는 경우 그대로 반환
    return city_name, False  # 변환 안됨

def get_demo_weather_data(city_name):
    """
    API 키가 작동하지 않을 때 사용할 데모 데이터
    """
    demo_data = {
        # 한국 주요 도시들
        "seoul": {
            "name": "Seoul",
            "sys": {"country": "KR", "sunrise": 1698106800, "sunset": 1698145200},
            "main": {
                "temp": 18.5,
                "feels_like": 17.2,
                "humidity": 65,
                "pressure": 1013,
                "temp_min": 15.0,
                "temp_max": 22.0
            },
            "weather": [{"description": "구름조금", "icon": "02d"}],
            "wind": {"speed": 2.5},
            "cod": 200
        },
        "busan": {
            "name": "Busan",
            "sys": {"country": "KR", "sunrise": 1698106900, "sunset": 1698145300},
            "main": {
                "temp": 20.1,
                "feels_like": 19.8,
                "humidity": 72,
                "pressure": 1015,
                "temp_min": 17.0,
                "temp_max": 23.0
            },
            "weather": [{"description": "맑음", "icon": "01d"}],
            "wind": {"speed": 3.1},
            "cod": 200
        },
        "incheon": {
            "name": "Incheon", 
            "sys": {"country": "KR", "sunrise": 1698106750, "sunset": 1698145150},
            "main": {
                "temp": 17.8,
                "feels_like": 16.9,
                "humidity": 68,
                "pressure": 1012,
                "temp_min": 14.0,
                "temp_max": 21.0
            },
            "weather": [{"description": "흐림", "icon": "04d"}],
            "wind": {"speed": 2.8},
            "cod": 200
        },
        "daegu": {
            "name": "Daegu",
            "sys": {"country": "KR", "sunrise": 1698107000, "sunset": 1698145400},
            "main": {
                "temp": 19.3,
                "feels_like": 18.7,
                "humidity": 61,
                "pressure": 1016,
                "temp_min": 16.0,
                "temp_max": 22.0
            },
            "weather": [{"description": "맑음", "icon": "01d"}],
            "wind": {"speed": 2.2},
            "cod": 200
        },
        "daejeon": {
            "name": "Daejeon",
            "sys": {"country": "KR", "sunrise": 1698106850, "sunset": 1698145250},
            "main": {
                "temp": 18.7,
                "feels_like": 17.9,
                "humidity": 64,
                "pressure": 1014,
                "temp_min": 15.0,
                "temp_max": 21.0
            },
            "weather": [{"description": "구름조금", "icon": "02d"}],
            "wind": {"speed": 2.1},
            "cod": 200
        },
        "gwangju": {
            "name": "Gwangju",
            "sys": {"country": "KR", "sunrise": 1698107100, "sunset": 1698145500},
            "main": {
                "temp": 20.5,
                "feels_like": 19.8,
                "humidity": 70,
                "pressure": 1013,
                "temp_min": 17.0,
                "temp_max": 23.0
            },
            "weather": [{"description": "맑음", "icon": "01d"}],
            "wind": {"speed": 2.9},
            "cod": 200
        },
        "ulsan": {
            "name": "Ulsan",
            "sys": {"country": "KR", "sunrise": 1698107050, "sunset": 1698145450},
            "main": {
                "temp": 19.8,
                "feels_like": 19.2,
                "humidity": 69,
                "pressure": 1015,
                "temp_min": 16.0,
                "temp_max": 22.0
            },
            "weather": [{"description": "구름많음", "icon": "03d"}],
            "wind": {"speed": 3.3},
            "cod": 200
        },
        "suwon": {
            "name": "Suwon",
            "sys": {"country": "KR", "sunrise": 1698106780, "sunset": 1698145180},
            "main": {
                "temp": 18.2,
                "feels_like": 17.5,
                "humidity": 66,
                "pressure": 1013,
                "temp_min": 15.0,
                "temp_max": 21.0
            },
            "weather": [{"description": "구름조금", "icon": "02d"}],
            "wind": {"speed": 2.4},
            "cod": 200
        },
        "chuncheon": {
            "name": "Chuncheon",
            "sys": {"country": "KR", "sunrise": 1698106700, "sunset": 1698145100},
            "main": {
                "temp": 16.1,
                "feels_like": 15.3,
                "humidity": 71,
                "pressure": 1011,
                "temp_min": 12.0,
                "temp_max": 19.0
            },
            "weather": [{"description": "안개", "icon": "50d"}],
            "wind": {"speed": 1.8},
            "cod": 200
        },
        "cheongju": {
            "name": "Cheongju",
            "sys": {"country": "KR", "sunrise": 1698106820, "sunset": 1698145220},
            "main": {
                "temp": 17.9,
                "feels_like": 17.1,
                "humidity": 67,
                "pressure": 1012,
                "temp_min": 14.0,
                "temp_max": 20.0
            },
            "weather": [{"description": "구름많음", "icon": "03d"}],
            "wind": {"speed": 2.3},
            "cod": 200
        },
        "jeonju": {
            "name": "Jeonju",
            "sys": {"country": "KR", "sunrise": 1698107050, "sunset": 1698145450},
            "main": {
                "temp": 19.4,
                "feels_like": 18.8,
                "humidity": 68,
                "pressure": 1014,
                "temp_min": 16.0,
                "temp_max": 22.0
            },
            "weather": [{"description": "맑음", "icon": "01d"}],
            "wind": {"speed": 2.6},
            "cod": 200
        },
        "jeju": {
            "name": "Jeju",
            "sys": {"country": "KR", "sunrise": 1698107200, "sunset": 1698145600},
            "main": {
                "temp": 22.3,
                "feels_like": 21.9,
                "humidity": 75,
                "pressure": 1016,
                "temp_min": 19.0,
                "temp_max": 25.0
            },
            "weather": [{"description": "구름조금", "icon": "02d"}],
            "wind": {"speed": 4.1},
            "cod": 200
        },
        "kimpo": {
            "name": "김포",
            "sys": {"country": "KR", "sunrise": 1698106770, "sunset": 1698145170},
            "main": {
                "temp": 17.5,
                "feels_like": 16.8,
                "humidity": 67,
                "pressure": 1012,
                "temp_min": 14.0,
                "temp_max": 20.0
            },
            "weather": [{"description": "구름많음", "icon": "03d"}],
            "wind": {"speed": 2.6},
            "cod": 200
        },
        
        # 해외 도시들
        "tokyo": {
            "name": "Tokyo",
            "sys": {"country": "JP", "sunrise": 1698106200, "sunset": 1698144600},
            "main": {
                "temp": 21.3,
                "feels_like": 20.8,
                "humidity": 58,
                "pressure": 1018,
                "temp_min": 18.0,
                "temp_max": 24.0
            },
            "weather": [{"description": "맑음", "icon": "01d"}],
            "wind": {"speed": 1.8},
            "cod": 200
        },
        "new york": {
            "name": "New York",
            "sys": {"country": "US", "sunrise": 1698142800, "sunset": 1698180000},
            "main": {
                "temp": 16.2,
                "feels_like": 15.1,
                "humidity": 72,
                "pressure": 1010,
                "temp_min": 12.0,
                "temp_max": 19.0
            },
            "weather": [{"description": "흐림", "icon": "04d"}],
            "wind": {"speed": 3.2},
            "cod": 200
        },
        "london": {
            "name": "London",
            "sys": {"country": "GB", "sunrise": 1698142200, "sunset": 1698179400},
            "main": {
                "temp": 12.8,
                "feels_like": 11.5,
                "humidity": 78,
                "pressure": 1008,
                "temp_min": 9.0,
                "temp_max": 15.0
            },
            "weather": [{"description": "비", "icon": "10d"}],
            "wind": {"speed": 4.2},
            "cod": 200
        },
        "paris": {
            "name": "Paris",
            "sys": {"country": "FR", "sunrise": 1698142500, "sunset": 1698179700},
            "main": {
                "temp": 14.6,
                "feels_like": 13.9,
                "humidity": 68,
                "pressure": 1012,
                "temp_min": 11.0,
                "temp_max": 17.0
            },
            "weather": [{"description": "구름많음", "icon": "03d"}],
            "wind": {"speed": 2.8},
            "cod": 200
        }
    }
    
    return demo_data.get(city_name.lower(), None)

def get_demo_forecast_data(city_name):
    """5일 날씨 예보 데모 데이터"""
    import random
    from datetime import timedelta
    
    base_demo_data = {
        "seoul": {"temp": 18.5, "icon": "02d", "desc": "구름조금"},
        "busan": {"temp": 20.1, "icon": "01d", "desc": "맑음"},
        "incheon": {"temp": 17.8, "icon": "04d", "desc": "흐림"},
        "daegu": {"temp": 19.3, "icon": "01d", "desc": "맑음"},
        "daejeon": {"temp": 18.7, "icon": "02d", "desc": "구름조금"},
        "gwangju": {"temp": 20.5, "icon": "01d", "desc": "맑음"},
        "ulsan": {"temp": 19.8, "icon": "03d", "desc": "구름많음"},
        "suwon": {"temp": 18.2, "icon": "02d", "desc": "구름조금"},
        "chuncheon": {"temp": 16.1, "icon": "50d", "desc": "안개"},
        "cheongju": {"temp": 17.9, "icon": "03d", "desc": "구름많음"},
        "jeonju": {"temp": 19.4, "icon": "01d", "desc": "맑음"},
        "jeju": {"temp": 22.3, "icon": "02d", "desc": "구름조금"},
        "kimpo": {"temp": 17.5, "icon": "03d", "desc": "구름많음"},
        "tokyo": {"temp": 21.3, "icon": "01d", "desc": "맑음"},
        "new york": {"temp": 16.2, "icon": "04d", "desc": "흐림"},
        "london": {"temp": 12.8, "icon": "10d", "desc": "비"},
        "paris": {"temp": 14.6, "icon": "03d", "desc": "구름많음"}
    }
    
    base_data = base_demo_data.get(city_name.lower())
    if not base_data:
        return None
    
    # 5일간의 예보 데이터 생성
    forecast_data = []
    today = datetime.now()
    
    weather_patterns = [
        {"icon": "01d", "desc": "맑음", "description": "맑음"},
        {"icon": "02d", "desc": "구름조금", "description": "구름조금"},
        {"icon": "03d", "desc": "구름많음", "description": "구름많음"},
        {"icon": "04d", "desc": "흐림", "description": "흐림"},
        {"icon": "09d", "desc": "소나기", "description": "소나기"},
        {"icon": "10d", "desc": "비", "description": "비"},
        {"icon": "13d", "desc": "눈", "description": "눈"},
        {"icon": "50d", "desc": "안개", "description": "안개"}
    ]
    
    for i in range(5):
        date = today + timedelta(days=i+1)
        temp_variation = random.uniform(-3, 3)
        
        # 시간대별 예보 (하루에 8번, 3시간 간격)
        day_forecasts = []
        for j in range(8):
            hour_temp = base_data["temp"] + temp_variation + random.uniform(-2, 2)
            weather = random.choice(weather_patterns)
            
            day_forecasts.append({
                "dt": int((date + timedelta(hours=j*3)).timestamp()),
                "main": {
                    "temp": round(hour_temp, 1),
                    "temp_min": round(hour_temp - 2, 1),
                    "temp_max": round(hour_temp + 2, 1),
                    "humidity": random.randint(50, 80)
                },
                "weather": [weather],
                "wind": {"speed": round(random.uniform(1, 5), 1)},
                "dt_txt": (date + timedelta(hours=j*3)).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        forecast_data.extend(day_forecasts)
    
    return {
        "cod": "200",
        "cnt": len(forecast_data),
        "list": forecast_data,
        "city": {
            "name": "김포" if city_name.lower() == "kimpo" else city_name.title(), 
            "country": "KR" if city_name.lower() in ["seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "ulsan", "suwon", "chuncheon", "cheongju", "jeonju", "jeju", "kimpo"] else "US"
        }
    }

def get_location_by_ip():
    """IP 주소를 기반으로 대략적인 위치를 가져옵니다"""
    try:
        # 무료 IP 지리 정보 서비스 사용
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'city': data['city'],
                    'country': data['country']
                }
    except:
        pass
    return None

def get_forecast_by_coordinates(lat, lon):
    """위도/경도 좌표를 사용하여 5일 예보 데이터를 가져옵니다"""
    
    # API 상태 확인
    api_status = check_api_key_status()
    
    # API가 활성화된 경우 실제 API 호출 시도
    if api_status == 'active':
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'kr'
            }
            
            with st.spinner('🌐 5일 예보 데이터를 가져오는 중...'):
                response = requests.get(FORECAST_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ 5일 예보 데이터를 성공적으로 가져왔습니다!")
                return data
            else:
                st.warning("⚠️ 예보 API 오류 발생. 데모 모드로 전환합니다.")
                
        except requests.exceptions.Timeout:
            st.warning("⏱️ 예보 요청 시간 초과. 데모 모드로 전환합니다.")
        except requests.exceptions.RequestException as e:
            st.warning(f"🌐 예보 네트워크 오류. 데모 모드로 전환합니다: {str(e)}")
    
    # 데모 모드 - 서울 예보 데이터 반환
    demo_data = get_demo_forecast_data("seoul")
    if demo_data:
        if api_status == 'invalid':
            st.warning("🔑 API 키가 유효하지 않습니다. 기본 위치(서울) 예보 데모 모드로 실행됩니다.")
        elif api_status == 'network_error':
            st.warning("🌐 네트워크 연결 문제. 기본 위치(서울) 예보 데모 모드로 실행됩니다.")
        
        st.info("✨ 기본 위치(서울) 예보 데모 데이터를 사용합니다.")
        return demo_data
    
    return None

def get_forecast_data(city_name):
    """도시명을 사용하여 5일 예보 데이터를 가져옵니다"""
    
    # 김포/김포시의 경우 데모 데이터 우선 사용
    if city_name.strip() in ["김포", "김포시"]:
        demo_data = get_demo_forecast_data("kimpo")
        if demo_data:
            st.info(f"'{city_name}' 전용 5일 예보 데모 데이터를 사용합니다.")
            return demo_data
        else:
            st.error(f"'{city_name}' 예보 데모 데이터를 찾을 수 없습니다.")
            return None
    
    # 한글 도시명 변환
    english_city, was_converted = convert_korean_to_english_city(city_name)
    
    if was_converted:
        st.info(f"🔄 '{city_name}' → '{english_city}'로 변환하여 예보를 검색합니다.")
    
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
            
            with st.spinner('🌐 5일 예보 데이터를 가져오는 중...'):
                response = requests.get(FORECAST_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ 5일 예보 데이터를 성공적으로 가져왔습니다!")
                return data
            elif response.status_code == 404:
                st.error(f"'{city_name}' 도시의 예보를 찾을 수 없습니다.")
                return None
            else:
                st.warning("⚠️ 예보 API 오류 발생. 데모 모드로 전환합니다.")
                
        except requests.exceptions.Timeout:
            st.warning("⏱️ 예보 요청 시간 초과. 데모 모드로 전환합니다.")
        except requests.exceptions.RequestException as e:
            st.warning(f"🌐 예보 네트워크 오류. 데모 모드로 전환합니다: {str(e)}")
    
    # 데모 모드 실행
    demo_data = get_demo_forecast_data(english_city)
    if demo_data:
        if api_status == 'invalid':
            st.warning("🔑 API 키가 유효하지 않습니다. 예보 데모 모드로 실행됩니다.")
        elif api_status == 'network_error':
            st.warning("🌐 네트워크 연결 문제. 예보 데모 모드로 실행됩니다.")
        
        st.info("✨ 예보 데모 데이터를 사용하여 5일 예보를 표시합니다.")
        return demo_data
    else:
        available_cities = "서울, 부산, 인천, 대구, 대전, 광주, 울산, 수원, 춘천, 청주, 전주, 제주, 김포, Tokyo, New York, London, Paris"
        st.error(f"😔 '{city_name}'에 대한 예보 데이터가 없습니다.")
        st.info(f"**사용 가능한 예보 도시**: {available_cities}")
        return None

def get_weather_by_coordinates(lat, lon):
    """위도/경도 좌표를 사용하여 날씨 데이터를 가져옵니다"""
    
    # API 상태 확인
    api_status = check_api_key_status()
    
    # API가 활성화된 경우 실제 API 호출 시도
    if api_status == 'active':
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'kr'
            }
            
            with st.spinner('🌐 현재 위치의 실시간 날씨 데이터를 가져오는 중...'):
                response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ 현재 위치의 실시간 날씨 데이터를 성공적으로 가져왔습니다!")
                return data
            else:
                st.warning("⚠️ API 오류 발생. 기본 위치(서울)로 데모 모드 실행합니다.")
                
        except requests.exceptions.Timeout:
            st.warning("⏱️ 요청 시간 초과. 기본 위치(서울)로 데모 모드 실행합니다.")
        except requests.exceptions.RequestException as e:
            st.warning(f"🌐 네트워크 오류. 기본 위치(서울)로 데모 모드 실행합니다: {str(e)}")
    
    # 데모 모드 - 서울 데이터 반환
    demo_data = get_demo_weather_data("seoul")
    if demo_data:
        if api_status == 'invalid':
            st.warning("🔑 API 키가 유효하지 않습니다. 기본 위치(서울)로 데모 모드 실행됩니다.")
        elif api_status == 'network_error':
            st.warning("🌐 네트워크 연결 문제. 기본 위치(서울)로 데모 모드 실행됩니다.")
        
        st.info("✨ 기본 위치(서울) 데모 데이터를 사용하여 날씨 정보를 표시합니다.")
        return demo_data
    
    return None

def get_weather_data(city_name):
    """
    OpenWeather API를 사용하여 도시의 날씨 정보를 가져옵니다.
    한글 도시명을 자동으로 영어로 변환합니다.
    """
    try:
        # 김포/김포시의 경우 데모 데이터 우선 사용
        if city_name.strip() in ["김포", "김포시"]:
            demo_data = get_demo_weather_data("kimpo")
            if demo_data:
                st.info(f"'{city_name}' 전용 데모 데이터를 사용하여 날씨 정보를 표시합니다.")
                return demo_data
        
        # 한글 도시명을 영어로 변환
        english_city, was_converted = convert_korean_to_english_city(city_name)
        
        if was_converted:
            st.info(f"'{city_name}' → '{english_city}'로 변환하여 검색합니다.")
        
        # API 요청 URL 구성
        params = {
            'q': english_city,
            'appid': API_KEY,
            'units': 'metric',  # 섭씨 온도 사용
            'lang': 'kr'  # 한국어 설명
        }
        
        response = requests.get(BASE_URL, params=params)
        
        # HTTP 상태 코드별 세부 오류 처리
        if response.status_code == 401:
            st.warning("🔑 **API 키 오류**: API 키가 유효하지 않습니다.")
            st.info("📄 **데모 모드로 전환**: 샘플 데이터를 표시합니다.")
            st.info("• API 키가 올바른지 확인해주세요")
            st.info("• API 키가 활성화되었는지 확인 (최대 2시간 소요)")
            
            # 데모 데이터 반환 (영어 도시명으로 검색)
            demo_data = get_demo_weather_data(english_city)
            if demo_data:
                st.success("✨ 데모 데이터를 사용하여 날씨 정보를 표시합니다.")
                st.info("🔄 실제 데이터를 보려면 새로운 API 키가 필요합니다.")
                return demo_data
            else:
                korean_cities = "서울, 부산, 인천, 대구, 대전, 광주, 울산, 수원, 춘천, 청주, 전주, 제주, 김포"
                available_cities = f"{korean_cities}, Tokyo, New York, London, Paris"
                st.error(f"😔 '{city_name}'에 대한 데모 데이터가 없습니다.")
                st.info(f"**사용 가능한 데모 도시**: {available_cities}")
                return None
        elif response.status_code == 404:
            st.error(f"**도시 검색 오류**: '{city_name}' 도시를 찾을 수 없습니다.")
            st.error("• 도시명을 영어로 입력해주세요")
            st.error("• 철자를 확인해주세요")
            return None
        elif response.status_code == 429:
            st.error("**API 한도 초과**: 잠시 후 다시 시도해주세요.")
            return None
        
        response.raise_for_status()  # 기타 HTTP 에러 체크
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 **네트워크 오류**: {e}")
        st.error("• 인터넷 연결을 확인해주세요")
        return None
    except json.JSONDecodeError:
        st.error("📄 **응답 처리 오류**: API 응답을 처리하는 중 오류가 발생했습니다.")
        return None

def display_forecast_info(forecast_data):
    """5일 예보 정보를 화면에 표시합니다"""
    if not forecast_data:
        return
    
    city_name = forecast_data['city']['name']
    country = forecast_data['city']['country']
    
    st.header(f"📅 {city_name}, {country} - 5일 예보")
    
    # 🎯 차트 먼저 표시
    chart = create_forecast_chart(forecast_data)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # 일별로 데이터 그룹화
    daily_forecasts = {}
    
    for item in forecast_data['list']:
        date_str = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
        
        if date_str not in daily_forecasts:
            daily_forecasts[date_str] = []
        
        daily_forecasts[date_str].append(item)
    
    # 날짜별로 정렬
    sorted_dates = sorted(daily_forecasts.keys())
    
    # 5일치만 표시
    for i, date_str in enumerate(sorted_dates[:5]):
        day_data = daily_forecasts[date_str]
        
        # 해당 날짜의 최고/최저 온도 계산
        temps = [item['main']['temp'] for item in day_data]
        min_temp = min(temps)
        max_temp = max(temps)
        
        # 가장 빈번한 날씨 상태 찾기
        weather_counts = {}
        for item in day_data:
            # description 또는 desc 키를 처리
            desc = item['weather'][0].get('description', item['weather'][0].get('desc', '알 수 없음'))
            icon = item['weather'][0]['icon']
            weather_counts[desc] = weather_counts.get(desc, 0) + 1
        
        most_common_weather = max(weather_counts, key=weather_counts.get)
        
        # 대표 아이콘 (가장 빈번한 날씨의 아이콘)
        representative_icon = None
        for item in day_data:
            item_desc = item['weather'][0].get('description', item['weather'][0].get('desc', '알 수 없음'))
            if item_desc == most_common_weather:
                representative_icon = item['weather'][0]['icon']
                break
        
        # 날짜 표시
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        weekday = weekdays[date_obj.weekday()]
        
        # 카드 형태로 표시
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])
            
            with col1:
                st.subheader(f"📅 {date_obj.strftime('%m/%d')} ({weekday})")
            
            with col2:
                if representative_icon:
                    icon_url = f"http://openweathermap.org/img/wn/{representative_icon}@2x.png"
                    st.image(icon_url, width=80)
            
            with col3:
                st.write(f"**{most_common_weather}**")
                
                # 평균 습도 계산
                avg_humidity = sum(item['main']['humidity'] for item in day_data) // len(day_data)
                st.write(f"💧 습도: {avg_humidity}%")
            
            with col4:
                st.metric(
                    label="🌡️ 온도",
                    value=f"{max_temp:.1f}°C",
                    delta=f"최저 {min_temp:.1f}°C"
                )
            
            with col5:
                # 평균 풍속 계산
                avg_wind = sum(item['wind']['speed'] for item in day_data) / len(day_data)
                st.write(f"**🌪️ 풍속**")
                st.write(f"{avg_wind:.1f} m/s")
        
        # 시간대별 상세 정보 (펼치기/접기)
        with st.expander(f"🕐 {date_obj.strftime('%m/%d')} 시간대별 상세 예보"):
            
            # 하루를 4개 시간대로 나누어 표시
            time_periods = [
                ("🌅 새벽 (00-06시)", [item for item in day_data if 0 <= datetime.fromtimestamp(item['dt']).hour < 6]),
                ("☀️ 오전 (06-12시)", [item for item in day_data if 6 <= datetime.fromtimestamp(item['dt']).hour < 12]),
                ("🌞 오후 (12-18시)", [item for item in day_data if 12 <= datetime.fromtimestamp(item['dt']).hour < 18]),
                ("🌙 저녁 (18-24시)", [item for item in day_data if 18 <= datetime.fromtimestamp(item['dt']).hour < 24])
            ]
            
            cols = st.columns(4)
            
            for j, (period_name, period_data) in enumerate(time_periods):
                if period_data:  # 해당 시간대에 데이터가 있는 경우
                    with cols[j]:
                        st.write(f"**{period_name}**")
                        
                        # 해당 시간대의 평균 온도
                        avg_temp = sum(item['main']['temp'] for item in period_data) / len(period_data)
                        st.write(f"🌡️ {avg_temp:.1f}°C")
                        
                        # 가장 빈번한 날씨
                        period_weather = {}
                        for item in period_data:
                            desc = item['weather'][0].get('description', item['weather'][0].get('desc', '알 수 없음'))
                            period_weather[desc] = period_weather.get(desc, 0) + 1
                        
                        if period_weather:
                            common_weather = max(period_weather, key=period_weather.get)
                            st.write(f"☁️ {common_weather}")
        
        st.markdown("---")

def create_forecast_chart(forecast_data):
    """5일 예보 데이터를 차트로 변환합니다"""
    if not forecast_data or 'list' not in forecast_data:
        return None
    
    dates = []
    temps = []
    humidity = []
    
    # 일별 데이터 추출 (하루에 하나씩만)
    seen_dates = set()
    
    for item in forecast_data['list']:
        date_str = datetime.fromtimestamp(item['dt']).strftime('%m/%d')
        
        if date_str not in seen_dates:
            dates.append(date_str)
            temps.append(item['main']['temp'])
            humidity.append(item['main']['humidity'])
            seen_dates.add(date_str)
            
            if len(dates) >= 5:  # 5일치만
                break
    
    # 온도 차트 생성
    fig = go.Figure()
    
    # 온도 라인
    fig.add_trace(go.Scatter(
        x=dates, 
        y=temps,
        mode='lines+markers',
        name='온도 (°C)',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    # 습도 라인 (보조축)
    fig.add_trace(go.Scatter(
        x=dates,
        y=humidity,
        mode='lines+markers',
        name='습도 (%)',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        title='📊 5일 날씨 트렌드',
        xaxis_title='날짜',
        yaxis_title='온도 (°C)',
        yaxis2=dict(
            title='습도 (%)',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def display_weather_info(weather_data):
    """
    날씨 정보를 Streamlit 화면에 표시합니다.
    """
    if not weather_data:
        return
    
    # 날씨별 배경색 적용
    bg_color = get_weather_background_color(weather_data)
    st.markdown(f"""
    <style>
    .weather-container {{
        background: linear-gradient(135deg, {bg_color} 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # 기본 정보 추출
    city_name = weather_data['name']
    country = weather_data['sys']['country']
    temperature = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    description = weather_data['weather'][0].get('description', weather_data['weather'][0].get('desc', ''))
    icon = weather_data['weather'][0]['icon']
    wind_speed = weather_data['wind']['speed']
    
    # 배경색이 적용된 컨테이너로 감싸기
    with st.container():
        st.markdown('<div class="weather-container">', unsafe_allow_html=True)
        
        # 날씨 정보 표시
        st.header(f"🌍 {city_name}, {country}")
        
        # 🎯 실생활 조언 먼저 표시
        advice_list = get_weather_advice(weather_data)
        
        # 디버그 정보 (임시)
        st.write(f"**디버그**: 온도 {temperature}°C, 날씨: {description}")
        st.write(f"**디버그**: 조언 개수: {len(advice_list)}")
        
        if advice_list:
            st.subheader("오늘의 날씨 조언")
            for advice in advice_list:
                st.info(advice)
        else:
            st.warning("조언을 생성하지 못했습니다.")
        
        # 메인 날씨 정보 컬럼으로 배치
        col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌡️ 현재 온도",
            value=f"{temperature:.1f}°C",
            delta=f"체감온도 {feels_like:.1f}°C"
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
    
    # 날씨 상태 및 아이콘
    st.subheader("☁️ 날씨 상태")
    
    # OpenWeather 아이콘 URL
    icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(icon_url, width=100)
    with col2:
        st.write(f"**{description.title()}**")
        st.write(f"**기압:** {pressure} hPa")
    
    # 추가 정보
    st.subheader("📊 상세 정보")
    
    # 온도 범위 (만약 API에서 제공한다면)
    if 'temp_min' in weather_data['main'] and 'temp_max' in weather_data['main']:
        temp_min = weather_data['main']['temp_min']
        temp_max = weather_data['main']['temp_max']
        st.write(f"**최저/최고 온도:** {temp_min:.1f}°C / {temp_max:.1f}°C")
    
    # 일출/일몰 시간
    if 'sunrise' in weather_data['sys'] and 'sunset' in weather_data['sys']:
        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🌅 **일출:** {sunrise}")
        with col2:
            st.write(f"🌇 **일몰:** {sunset}")
        
        st.markdown('</div>', unsafe_allow_html=True)  # 컨테이너 닫기

def main():
    """
    메인 애플리케이션 함수
    """
    # 페이지 설정
    st.set_page_config(
        page_title="날씨 정보 앱",
        page_icon="■",
        layout="wide"
    )
    
    # API 키 설정 확인
    if not check_api_key_configuration():
        display_api_key_setup_guide()
        return
    
    # 앱 제목
    st.title("WEATHER INFO | Real-time Weather Application")
    st.markdown("---")
    
    # 도시 선택 섹션 (최우선)
    st.subheader("CITY SELECTION | 도시 선택")
    
    # 현재 선택된 도시 표시
    if st.session_state.selected_city:
        st.success(f"현재 선택된 도시: **{st.session_state.selected_city}**")
    else:
        st.warning("도시를 선택해주세요!")
    
    # 도시 선택 옵션들을 탭으로 구성
    tab1, tab2, tab3 = st.tabs(["도시 목록", "지도에서 선택", "직접 입력"])
    
    with tab1:
        st.markdown("**주요 도시에서 선택하세요:**")
        
        # 한국 도시들을 5개 열로 배치
        col1, col2, col3, col4, col5 = st.columns(5)
        
        korean_cities = list(KOREAN_CITIES_COORDINATES.keys())
        for i, city in enumerate(korean_cities):
            col = [col1, col2, col3, col4, col5][i % 5]
            with col:
                if st.button(f"{city}", key=f"select_{city}", type="primary" if st.session_state.selected_city == city else "secondary", use_container_width=True):
                    st.session_state.selected_city = city
                    st.success(f"{city} 선택됨!")
                    st.rerun()
        
        # 국제 도시들
        st.markdown("**국제 도시:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        international_cities = ["Tokyo", "New York"]
        for i, city in enumerate(international_cities):
            col = [col1, col2, col3, col4, col5][i % 5]
            with col:
                if st.button(f"{city}", key=f"select_intl_{city}", type="primary" if st.session_state.selected_city == city else "secondary", use_container_width=True):
                    st.session_state.selected_city = city
                    st.success(f"{city} 선택됨!")
                    st.rerun()
    
    with tab2:
        st.markdown("**지도에서 도시를 선택하세요:**")
        map_city_select = st.selectbox(
            "도시 선택:",
            ["선택하세요"] + list(KOREAN_CITIES_COORDINATES.keys()),
            key="main_city_select",
            index=0 if not st.session_state.selected_city else (list(KOREAN_CITIES_COORDINATES.keys()).index(st.session_state.selected_city) + 1 if st.session_state.selected_city in KOREAN_CITIES_COORDINATES else 0)
        )
        
        if map_city_select and map_city_select != "선택하세요":
            if st.button(f"{map_city_select} 선택", type="primary", key="confirm_map_select"):
                st.session_state.selected_city = map_city_select
                st.success(f"{map_city_select} 선택됨!")
                st.rerun()
    
    with tab3:
        st.markdown("**도시명을 직접 입력하세요:**")
        city_input = st.text_input(
            "도시명 입력:",
            placeholder="예: 부천, 서울, Seoul, Tokyo",
            key="direct_city_input"
        )
        
        if st.button("도시 선택", type="primary", key="confirm_direct_input") and city_input:
            st.session_state.selected_city = city_input
            st.success(f"{city_input} 선택됨!")
            st.rerun()
    
    st.markdown("---")
    
    # 사이드바에 설명 추가
    st.sidebar.title("USAGE GUIDE")
    st.sidebar.markdown("""
    **4가지 방법으로 날씨 조회:**
    
    **1. �️ 전국 날씨 지도**
    - 한국 전체 날씨를 한눈에!
    - 온도별 색상 표시
    
    **2. �📍 현재 위치 기반**
    - '내 위치 날씨' 버튼 클릭
    - IP 주소로 위치 자동 감지
    
    **3. 🗺️ 좌표 직접 입력**
    - '좌표 입력' 버튼으로 위도/경도 입력
    - 정확한 위치 지정 가능
    
    **4. 🏙️ 도시명 입력**
    - **한글**: 서울, 부산, 인천, 대구, 대전, 김포
    - **영어**: Seoul, Busan, Tokyo, New York
    """)
    
    # 선택된 도시의 현재 날씨 표시 (우선 섹션)
    if st.session_state.selected_city:
        st.markdown("---")
        st.subheader(f"{st.session_state.selected_city} CURRENT WEATHER")
        
        weather_data = get_weather_data(st.session_state.selected_city)
        if weather_data:
            # 메인 날씨 정보를 2개 열로 구성
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 주요 날씨 정보
                temp = weather_data['main']['temp']
                desc = weather_data['weather'][0].get('description', 
                      weather_data['weather'][0].get('desc', ''))
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                feels_like = weather_data['main']['feels_like']
                
                # 큰 온도 표시
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(255, 214, 0, 0.2) 100%); border-radius: 15px; margin: 10px 0; border: 1px solid #ffd600;">
                    <h1 style="color: #000000; font-size: 4em; margin: 0;">{temp}°C</h1>
                    <h3 style="color: #000000; margin: 10px 0;">{desc}</h3>
                    <p style="color: #000000;">체감온도: {feels_like}°C</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 추가 정보
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("습도", f"{humidity}%")
                with metric_col2:
                    st.metric("풍속", f"{wind_speed} m/s")
            
            with col2:
                # 빠른 액션 버튼들
                st.markdown("**빠른 기능:**")
                
                # 5일 예보 버튼
                if st.button(f"{st.session_state.selected_city} 5일 예보", type="primary", key="main_forecast_btn"):
                    st.session_state.show_forecast[st.session_state.selected_city] = True
                    st.rerun()
                
                # AI 비서 빠른 질문
                st.markdown("**AI 빠른 질문:**")
                quick_questions = [
                    "외출하기 좋은 날씨인가요?",
                    "운동하기 어떤가요?",
                    "무엇을 입어야 할까요?"
                ]
                
                for question in quick_questions:
                    if st.button(question, key=f"quick_{question}", type="secondary"):
                        # AI 질문 처리 로직은 아래에서 처리됨
                        st.session_state.ai_question = question
                        st.rerun()
        
        # 시간별 날씨 섹션 추가 (날씨 데이터가 있을 때)
        if weather_data:
            st.markdown("---")
            st.subheader("⏰ 24시간 날씨 예보")
            
            # 5일 예보 데이터를 가져와서 오늘과 내일의 시간별 데이터 사용
            with st.spinner('시간별 날씨 데이터를 불러오는 중...'):
                forecast_data = get_forecast_data(st.session_state.selected_city)
            
            if forecast_data:
                # 오늘과 내일 24시간 데이터 추출
                hourly_data = []
                current_time = datetime.now()
                
                for item in forecast_data['list'][:8]:  # 24시간 (3시간 간격 8개)
                    forecast_time = datetime.fromtimestamp(item['dt'])
                    hourly_data.append({
                        'time': forecast_time.strftime('%H:%M'),
                        'temp': item['main']['temp'],
                        'desc': item['weather'][0].get('description', item['weather'][0].get('desc', '')),
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity'],
                        'wind': item['wind']['speed']
                    })
                
                # 시간별 날씨를 4개씩 2행으로 표시
                for row in range(2):
                    cols = st.columns(4)
                    for col_idx in range(4):
                        data_idx = row * 4 + col_idx
                        if data_idx < len(hourly_data):
                            hour_data = hourly_data[data_idx]
                            
                            with cols[col_idx]:
                                # 시간별 날씨 카드
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(255, 214, 0, 0.1) 100%);
                                    border: 1px solid #ffd600;
                                    border-radius: 10px;
                                    padding: 15px;
                                    text-align: center;
                                    margin: 5px 0;
                                ">
                                    <h4 style="color: #000000; margin: 0 0 10px 0;">{hour_data['time']}</h4>
                                    <p style="color: #000000; font-size: 1.5em; font-weight: bold; margin: 5px 0;">{hour_data['temp']:.1f}°C</p>
                                    <p style="color: #000000; margin: 5px 0; font-size: 0.9em;">{hour_data['desc']}</p>
                                    <p style="color: #666; margin: 5px 0; font-size: 0.8em;">습도: {hour_data['humidity']}%</p>
                                    <p style="color: #666; margin: 5px 0; font-size: 0.8em;">바람: {hour_data['wind']} m/s</p>
                                </div>
                                """, unsafe_allow_html=True)
                
                st.info("💡 3시간 간격으로 향후 24시간의 날씨를 보여줍니다!")
            else:
                # 예보 데이터를 못 가져왔을 때 기본 시간별 데이터 표시
                st.warning("실시간 시간별 데이터를 가져올 수 없어서 기본 예시를 보여드려요!")
                
                # 기본 시간별 데이터 생성 (현재 날씨 기반)
                current_temp = weather_data['main']['temp']
                current_desc = weather_data['weather'][0].get('description', 
                              weather_data['weather'][0].get('desc', ''))
                current_humidity = weather_data['main']['humidity']
                current_wind = weather_data['wind']['speed']
                
                basic_hourly_data = []
                for i in range(8):
                    hour = (datetime.now().hour + i * 3) % 24
                    temp_variation = random.uniform(-3, 3)  # 온도 변화
                    basic_hourly_data.append({
                        'time': f"{hour:02d}:00",
                        'temp': current_temp + temp_variation,
                        'desc': current_desc,
                        'humidity': max(30, min(90, current_humidity + random.randint(-10, 10))),
                        'wind': max(0, current_wind + random.uniform(-1, 1))
                    })
                
                # 시간별 날씨를 4개씩 2행으로 표시 (기본 데이터)
                for row in range(2):
                    cols = st.columns(4)
                    for col_idx in range(4):
                        data_idx = row * 4 + col_idx
                        if data_idx < len(basic_hourly_data):
                            hour_data = basic_hourly_data[data_idx]
                            
                            with cols[col_idx]:
                                # 시간별 날씨 카드
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(255, 214, 0, 0.1) 100%);
                                    border: 1px solid #ffd600;
                                    border-radius: 10px;
                                    padding: 15px;
                                    text-align: center;
                                    margin: 5px 0;
                                ">
                                    <h4 style="color: #000000; margin: 0 0 10px 0;">{hour_data['time']}</h4>
                                    <p style="color: #000000; font-size: 1.5em; font-weight: bold; margin: 5px 0;">{hour_data['temp']:.1f}°C</p>
                                    <p style="color: #000000; margin: 5px 0; font-size: 0.9em;">{hour_data['desc']}</p>
                                    <p style="color: #666; margin: 5px 0; font-size: 0.8em;">습도: {hour_data['humidity']}%</p>
                                    <p style="color: #666; margin: 5px 0; font-size: 0.8em;">바람: {hour_data['wind']:.1f} m/s</p>
                                </div>
                                """, unsafe_allow_html=True)
                
                st.info("💡 현재 날씨 기반의 예상 시간별 날씨입니다!")
        
        else:
            st.error(f"{st.session_state.selected_city}의 날씨 정보를 가져올 수 없습니다.")
    
    # 전국 날씨 지도 섹션 추가
    st.subheader("KOREA WEATHER MAP")
    st.info("마커를 클릭하면 각 도시의 상세 날씨 정보를 볼 수 있어요!")
    
    # 지도와 도시 검색을 함께 표시하는 컨테이너
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 지도 표시/숨기기 토글
        if st.button("전국 날씨 지도 보기/숨기기", type="secondary"):
            st.session_state.show_map = not st.session_state.get('show_map', False)
    
    with col2:
        # 지도에서 도시 검색
        if st.session_state.get('show_map', False):
            map_city_search = st.selectbox(
                "지도에서 도시 선택:",
                ["선택하세요"] + list(KOREAN_CITIES_COORDINATES.keys()),
                key="map_city_search"
            )
    
    # 지도 표시
    if st.session_state.get('show_map', False):
        col_map, col_weather = st.columns([3, 2])
        
        with col_map:
            with st.spinner("전국 날씨 지도를 생성하는 중..."):
                weather_map = create_korea_weather_map()
                # 선택된 도시가 있으면 해당 위치로 중심 이동
                if map_city_search and map_city_search != "선택하세요":
                    city_coords = KOREAN_CITIES_COORDINATES[map_city_search]
                    weather_map = create_korea_weather_map(center_city=map_city_search)
                
                map_data = st_folium(weather_map, width=500, height=400, key="weather_map")
        
        with col_weather:
            # 선택된 도시의 날씨 상세 정보
            if map_city_search and map_city_search != "선택하세요":
                st.markdown("### 선택된 도시 날씨")
                weather_data = get_weather_data(map_city_search)
                
                if weather_data:
                    # 간단한 날씨 정보 표시
                    temp = weather_data['main']['temp']
                    desc = weather_data['weather'][0].get('description', 
                          weather_data['weather'][0].get('desc', ''))
                    humidity = weather_data['main']['humidity']
                    wind_speed = weather_data['wind']['speed']
                    
                    st.metric("온도", f"{temp}°C")
                    st.metric("습도", f"{humidity}%")
                    st.metric("풍속", f"{wind_speed} m/s")
                    st.write(f"**날씨**: {desc}")
                    
                    # 5일 예보 버튼
                    if st.button(f"{map_city_search} 5일 예보", type="primary", key="map_forecast_btn"):
                        st.session_state.selected_city = map_city_search
                        st.session_state.show_forecast[map_city_search] = True
            else:
                st.info("왼쪽 드롭다운에서 도시를 선택하거나 지도의 마커를 클릭해보세요!")
        
        st.success("전국 13개 도시의 실시간 날씨를 확인하세요!")
        
        # 5일 예보 표시 (선택된 도시가 있고 예보 요청이 있는 경우)
        if (st.session_state.selected_city and 
            st.session_state.show_forecast.get(st.session_state.selected_city, False)):
            
            st.markdown("---")
            st.markdown("### 📅 선택된 도시 5일 예보")
            
            forecast_data = get_forecast_data(st.session_state.selected_city)
            if forecast_data:
                display_forecast_info(forecast_data)
    
    st.markdown("---")
    
    st.sidebar.markdown("---")
    st.sidebar.title("API KEY SETTINGS")
    st.sidebar.markdown("""
    **현재 API 키 상태: ❌ 비활성**
    
    **새 API 키 발급 방법:**
    
    1. [OpenWeather 회원가입](https://openweathermap.org/api)
    2. 이메일 인증 완료
    3. API Keys 페이지에서 키 생성
    4. 아래 코드에 새 키 입력:
    
    ```python
    API_KEY = "새로운_API_키"
    ```
    
    ⚠️ **주의사항:**
    - 새 계정 생성 후 API 키 활성화까지 최대 2시간 소요
    - 무료 계정: 1,000회/일 호출 제한
    
    **현재 데모 모드 사용 가능 도시:**
    - 서울, 부산, 인천, 대구, 대전, 광주, 울산, 수원, 춘천, 청주, 전주, 제주, 김포
    - Tokyo, New York, London, Paris
    """)
    
    # AI 날씨 비서 섹션 추가
    st.subheader("AI WEATHER ASSISTANT")
    st.info("자연스럽게 질문해보세요! AI가 날씨를 분석해서 답변드려요!")
    
    # AI 질문 입력
    ai_question = st.text_input(
        "궁금한 것을 자유롭게 질문하세요:",
        placeholder="예: 내일 소풍 가도 될까요? / 빨래 말리기 좋나요? / 무슨 옷 입을까요?",
        key="ai_question"
    )
    
    # 질문 예시 버튼들
    st.write("**질문 예시:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("빨래 말리기 좋나요?", use_container_width=True):
            ai_question = "빨래 말리기 좋나요?"
    
    with col2:
        if st.button("소풍 가도 될까요?", use_container_width=True):
            ai_question = "소풍 가도 될까요?"
    
    with col3:
        if st.button("무슨 옷 입을까요?", use_container_width=True):
            ai_question = "무슨 옷 입을까요?"
    
    with col4:
        if st.button("운동하기 어때요?", use_container_width=True):
            ai_question = "운동하기 어때요?"
    
    # 세션 상태에서 AI 질문 확인
    if hasattr(st.session_state, 'ai_question') and st.session_state.ai_question:
        ai_question = st.session_state.ai_question
        # 질문 처리 후 세션 상태 클리어
        st.session_state.ai_question = None
    
    # AI 답변 처리
    if ai_question:
        if st.session_state.selected_city:
            weather_data = get_weather_data(st.session_state.selected_city)
            city_name = st.session_state.selected_city
        else:
            # 기본적으로 서울 날씨 사용
            weather_data = get_weather_data("서울")
            city_name = "서울"
            
        if weather_data:
            ai_responses = weather_ai_assistant(ai_question, weather_data)
            
            st.markdown("---")
            if not st.session_state.selected_city:
                st.info(f"선택된 도시가 없어서 **{city_name}** 날씨 기준으로 답변드려요!")
            
            st.subheader("AI 비서의 답변:")
            
            for response in ai_responses:
                if response.startswith("**") or response.startswith("•"):
                    st.write(response)
                else:
                    st.success(response)
    
    st.markdown("---")
    
    # 날씨 일기 섹션 추가
    st.subheader("WEATHER DIARY")
    st.info("오늘 날씨와 함께 일기를 써보세요! 날씨와 기분이 함께 기록됩니다.")
    
    # 일기 쓰기와 보기 탭
    diary_tab1, diary_tab2 = st.tabs(["일기 쓰기", "일기 보기"])
    
    with diary_tab1:
        if st.session_state.selected_city:
            # 선택된 도시의 날씨 정보로 일기 쓰기
            weather_data = get_weather_data(st.session_state.selected_city)
            if weather_data:
                city_name = st.session_state.selected_city
                temp = weather_data['main']['temp']
                desc = weather_data['weather'][0].get('description', 
                      weather_data['weather'][0].get('desc', ''))
                
                st.write(f"**오늘의 날씨**: {city_name} | {temp}°C | {desc}")
                
                # 기분 선택
                mood_options = get_weather_mood_suggestions(weather_data)
                selected_mood = st.selectbox("오늘의 기분을 선택하세요:", mood_options)
                
                # 일기 작성
                diary_text = st.text_area(
                    "오늘의 일기를 써보세요:",
                    placeholder=f"오늘은 {desc} 날씨네요. 기분은 어떤가요? 무엇을 했나요?",
                    height=150
                )
                
                # 저장 버튼 (크고 중앙 배치)
                st.markdown("<br>", unsafe_allow_html=True)  # 위쪽 여백
                
                # 큰 버튼 스타일 
                st.markdown("""
                <style>
                div.stButton > button:first-child {
                    height: 3em;
                    font-size: 18px;
                    font-weight: bold;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # 중앙 배치를 위한 컬럼 (1:2:1 비율)  
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📝 일기 저장하기 ✨", type="primary", use_container_width=True, key="save_diary_btn"):
                        if diary_text.strip():
                            success, result = save_weather_diary(
                                city_name, weather_data, diary_text, selected_mood
                            )
                            if success:
                                st.success(f"일기가 저장되었습니다! 파일: {result}")
                                st.balloons()  # 축하 효과!
                            else:
                                st.error(f"저장 실패: {result}")
                        else:
                            st.warning("일기 내용을 입력해주세요!")
                
                st.markdown("<br>", unsafe_allow_html=True)  # 아래쪽 여백
        else:
            # 도시 선택 없이도 일기 쓰기 가능
            st.info("💡 날씨 정보와 함께 일기를 쓰려면 위의 '도시 선택'에서 먼저 도시를 선택해주세요!")
            
            # 기본 일기 쓰기 (날씨 정보 없이)
            st.write("**📝 오늘의 일기**")
            
            # 기분 선택 (기본 옵션)
            basic_moods = ["😊 좋음", "😐 보통", "😔 별로", "😴 피곤함", "😆 즐거움", "😤 짜증남"]
            selected_mood = st.selectbox("오늘의 기분을 선택하세요:", basic_moods)
            
            # 일기 작성
            diary_text = st.text_area(
                "오늘의 일기를 써보세요:",
                placeholder="오늘 하루는 어땠나요? 무엇을 했나요? 어떤 생각을 하셨나요?",
                height=150
            )
            
            # 저장 버튼 (크고 중앙 배치) - 도시 정보 없이도 저장
            st.markdown("<br>", unsafe_allow_html=True)  # 위쪽 여백
            
            # 큰 버튼 스타일 
            st.markdown("""
            <style>
            div.stButton > button:first-child {
                height: 3em;
                font-size: 18px;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 중앙 배치를 위한 컬럼 (1:2:1 비율)  
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📝 일기 저장하기 ✨", type="primary", use_container_width=True, key="save_basic_diary_btn"):
                    if diary_text.strip():
                        # 기본 날씨 정보 (도시 없음)
                        basic_weather = {
                            'name': '일반',
                            'main': {'temp': 0, 'humidity': 0},
                            'weather': [{'description': '날씨정보없음', 'desc': '날씨정보없음'}],
                            'wind': {'speed': 0}
                        }
                        success, result = save_weather_diary(
                            "일반일기", basic_weather, diary_text, selected_mood
                        )
                        if success:
                            st.success(f"일기가 저장되었습니다! 파일: {result}")
                            st.balloons()  # 축하 효과!
                        else:
                            st.error(f"저장 실패: {result}")
                    else:
                        st.warning("일기 내용을 입력해주세요!")
            
            st.markdown("<br>", unsafe_allow_html=True)  # 아래쪽 여백
            
            st.markdown("**💡 날씨 정보와 함께 일기를 쓰려면:**")
            st.markdown("- **도시 목록**: 주요 도시 버튼 클릭")
            st.markdown("- **지도에서 선택**: 드롭다운에서 선택") 
            st.markdown("- **직접 입력**: 도시명 직접 입력")
    
    with diary_tab2:
        # 저장된 일기들 보기
        diaries = load_weather_diaries()
        
        if diaries:
            st.write(f"**총 {len(diaries)}개의 일기가 있습니다**")
            
            # 날짜별 일기 선택
            diary_dates = [diary['date'] for diary in diaries]
            selected_date = st.selectbox("날짜 선택:", diary_dates)
            
            # 선택된 날짜의 일기 표시
            selected_diary = next((d for d in diaries if d['date'] == selected_date), None)
            if selected_diary:
                st.markdown("### 📖 일기 내용")
                
                # 날씨 일기 내용을 예쁘게 표시
                diary_content = selected_diary['content']
                
                # 스타일링된 박스로 표시
                st.markdown(f"""
                <div style="
                    background: rgba(25, 35, 126, 0.2);
                    border: 1px solid #42a5f5;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    white-space: pre-line;
                    font-family: 'Courier New', monospace;
                ">
                {diary_content}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("아직 작성된 일기가 없습니다. 첫 번째 날씨 일기를 써보세요!")
    
    st.markdown("---")
    
    # 현재 위치 기반 날씨 섹션
    st.subheader("CURRENT LOCATION WEATHER")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("🌐 IP 주소를 기반으로 대략적인 현재 위치의 날씨를 확인할 수 있습니다.")
    
    with col2:
        if st.button("내 위치 날씨", type="primary"):
            with st.spinner("🔍 현재 위치를 찾는 중..."):
                location_info = get_location_by_ip()
                
            if location_info:
                st.session_state.current_location_data = {
                    'location_info': location_info,
                    'show_weather': True
                }
            else:
                st.error("😔 현재 위치를 감지할 수 없습니다. 아래에서 도시명을 직접 입력해주세요.")
    
    # 현재 위치 날씨 결과를 전체 넓이로 표시
    if st.session_state.get('current_location_data', {}).get('show_weather', False):
        location_info = st.session_state.current_location_data['location_info']
        
        st.success(f"감지된 위치: {location_info['city']}, {location_info['country']}")
        
        weather_data = get_weather_by_coordinates(
            location_info['lat'], 
            location_info['lon']
        )
        
        if weather_data:
            st.markdown("---")
            st.subheader(f"{location_info['city']} 현재 날씨")
            display_weather_info(weather_data)
            
            # 현재 위치 5일 예보 버튼 (중앙에 배치)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📅 현재 위치 5일 예보", type="secondary", key="location_forecast_btn"):
                    forecast_data = get_forecast_by_coordinates(
                        location_info['lat'], 
                        location_info['lon']
                    )
                    if forecast_data:
                        st.session_state.current_location_forecast = {
                            'forecast_data': forecast_data,
                            'show_forecast': True
                        }
            
            st.markdown("---")
    
    # 현재 위치 5일 예보 결과를 전체 넓이로 표시
    if st.session_state.get('current_location_forecast', {}).get('show_forecast', False):
        forecast_data = st.session_state.current_location_forecast['forecast_data']
        st.markdown("---")
        display_forecast_info(forecast_data)
    
    with col3:
        if st.button("좌표 입력"):
            st.session_state.show_coordinate_input = not st.session_state.get('show_coordinate_input', False)
    
    # 좌표 직접 입력 옵션
    if st.session_state.get('show_coordinate_input', False):
        st.subheader("좌표로 날씨 조회")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            lat_input = st.number_input("위도 (Latitude)", 
                                       min_value=-90.0, max_value=90.0, 
                                       value=37.5665, step=0.0001, format="%.4f")
        
        with col2:
            lon_input = st.number_input("경도 (Longitude)", 
                                       min_value=-180.0, max_value=180.0, 
                                       value=126.9780, step=0.0001, format="%.4f")
        
        with col3:
            if st.button("좌표로 조회", type="secondary"):
                st.session_state.coordinate_weather_data = {
                    'lat': lat_input,
                    'lon': lon_input,
                    'show_weather': True
                }
        
        # 좌표 기반 날씨 결과를 전체 넓이로 표시
        if st.session_state.get('coordinate_weather_data', {}).get('show_weather', False):
            coord_data = st.session_state.coordinate_weather_data
            weather_data = get_weather_by_coordinates(coord_data['lat'], coord_data['lon'])
            if weather_data:
                st.markdown("---")
                st.subheader(f"좌표 ({coord_data['lat']:.4f}, {coord_data['lon']:.4f}) 날씨")
                display_weather_info(weather_data)
                
                # 좌표 기반 5일 예보 버튼 (중앙에 배치)
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("좌표 위치 5일 예보", type="secondary", key="coord_forecast_btn"):
                        forecast_data = get_forecast_by_coordinates(coord_data['lat'], coord_data['lon'])
                        if forecast_data:
                            st.session_state.coordinate_forecast = {
                                'forecast_data': forecast_data,
                                'show_forecast': True
                            }
                
                st.markdown("---")
        
        # 좌표 기반 5일 예보 결과를 전체 넓이로 표시
        if st.session_state.get('coordinate_forecast', {}).get('show_forecast', False):
            forecast_data = st.session_state.coordinate_forecast['forecast_data']
            st.markdown("---")
            display_forecast_info(forecast_data)
        
        st.caption("참고: 서울(37.5665, 126.9780), 부산(35.1796, 129.0756), 제주(33.4996, 126.5312)")
    
    st.markdown("---")
    

    
    # 푸터
    st.markdown("---")
    st.markdown("**데이터 제공:** OpenWeatherMap API")
    st.markdown("**마지막 업데이트:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()