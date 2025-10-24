# 🌤️ 날씨 웹앱 (Weather Web App)

Streamlit과 OpenWeather API를 사용하여 만든 실시간 날씨 정보 웹 애플리케이션입니다.

## 🚀 기능

- 전 세계 도시의 실시간 날씨 정보 조회
- 온도, 습도, 풍속, 기압 등 상세 정보 제공
- 날씨 아이콘과 상태 설명
- 일출/일몰 시간 정보
- 인기 도시 빠른 검색 버튼
- 반응형 웹 인터페이스

## 📋 요구사항

- Python 3.7 이상
- Streamlit
- Requests
- OpenWeather API 키

## 🛠️ 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd weather
   ```

2. **가상환경 생성 (선택사항)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경변수 설정**
   - 프로젝트 루트 디렉토리에 `.env` 파일 생성
   - `.env.example` 파일을 참고하여 설정
   - OpenWeather API에서 무료 API 키를 발급받으세요 ([API 키 발급](https://openweathermap.org/api))
   - `.env` 파일에 다음과 같이 추가:
   ```
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

5. **앱 실행**
   ```bash
   streamlit run app.py
   ```

6. **브라우저에서 확인**
   - 자동으로 브라우저가 열리거나 http://localhost:8501 에 접속하세요

## 📱 사용법

1. 웹 애플리케이션에 접속
2. 도시명을 영어로 입력 (예: Seoul, Tokyo, New York)
3. "날씨 조회" 버튼 클릭 또는 인기 도시 버튼 클릭
4. 실시간 날씨 정보 확인

## 🌍 지원 도시

- 한국: Seoul, Busan, Incheon, Daegu, Gwangju 등
- 일본: Tokyo, Osaka, Kyoto 등  
- 미국: New York, Los Angeles, Chicago 등
- 유럽: London, Paris, Berlin, Rome 등
- 기타 전 세계 주요 도시들

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **API**: OpenWeather API
- **HTTP Client**: Requests

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

이슈 리포트나 기능 개선 제안은 언제든지 환영합니다!