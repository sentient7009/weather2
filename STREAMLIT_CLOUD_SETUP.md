# 🔧 Streamlit Cloud 환경변수 설정 가이드

## 🚨 현재 문제: "API키가 설정되어 있지 않습니다"

이 오류는 Streamlit Cloud에서 환경변수가 설정되지 않아서 발생합니다.

## ✅ 해결 방법: Streamlit Cloud Secrets 설정

### 1단계: 앱 설정 페이지로 이동
1. 배포된 Streamlit 앱 페이지를 엽니다
2. 오른쪽 상단의 **⚙️ Settings** 버튼을 클릭합니다

### 2단계: Secrets 메뉴 찾기
1. 왼쪽 사이드바에서 **🔐 Secrets** 를 클릭합니다
2. 또는 **Advanced settings** → **Secrets** 경로로 이동

### 3단계: 환경변수 추가
텍스트 입력창에 다음 내용을 **정확히** 입력합니다:

```toml
OPENWEATHER_API_KEY = "your_actual_api_key_here"
```

⚠️ **주의사항**:
- 따옴표(" ") 포함해서 입력
- 대소문자 정확히 일치
- 등호(=) 앞뒤 공백 유지

### 4단계: OpenWeather API 키 발급

#### 4-1. 회원가입
1. [OpenWeather API](https://openweathermap.org/api) 접속
2. **Sign Up** 클릭하여 무료 회원가입
3. 이메일 인증 완료

#### 4-2. API 키 확인
1. 로그인 후 대시보드로 이동
2. **API Keys** 탭 클릭
3. **Default** API 키 복사 (또는 새로 생성)

#### 4-3. API 키 형태 확인
- 올바른 형태: `1234567890abcdef1234567890abcdef` (32자리 영숫자)
- 잘못된 형태: `YOUR_API_KEY_HERE`, `your_api_key_here`

### 5단계: Secrets에 API 키 입력
1. 복사한 API 키를 다음과 같이 입력:
```toml
OPENWEATHER_API_KEY = "1234567890abcdef1234567890abcdef"
```

2. **Save** 버튼 클릭

### 6단계: 앱 재시작 확인
- Streamlit Cloud가 자동으로 앱을 재시작합니다
- 1-2분 기다린 후 새로고침해보세요
- 에러 메시지가 사라지고 정상 작동해야 합니다

## 🔍 문제 해결

### API 키가 여전히 인식되지 않는 경우

1. **Secrets 형식 재확인**
   ```toml
   # 올바른 형식
   OPENWEATHER_API_KEY = "실제API키32자리"
   
   # 잘못된 형식들
   OPENWEATHER_API_KEY: "실제API키"      # 콜론 사용 금지
   OPENWEATHER_API_KEY="실제API키"       # 공백 없음 금지
   openweather_api_key = "실제API키"     # 대소문자 불일치
   ```

2. **API 키 유효성 확인**
   - 새로 발급받은 API 키는 2시간 후 활성화
   - 무료 계정은 1,000회/일 제한

3. **캐시 클리어**
   - 브라우저 새로고침 (Ctrl+F5)
   - Streamlit Cloud에서 앱 재시작

## 🎯 최종 확인 체크리스트

- [ ] OpenWeather API 계정 생성 완료
- [ ] 이메일 인증 완료
- [ ] API 키 복사 완료 (32자리 영숫자)
- [ ] Streamlit Cloud Secrets 설정 완료
- [ ] 형식 정확히 입력: `OPENWEATHER_API_KEY = "API키"`
- [ ] Save 버튼 클릭 완료
- [ ] 앱 새로고침 완료
- [ ] 에러 메시지 사라짐 확인

## 💡 추가 팁

- **로컬 테스트**: 배포 전에 로컬에서 `.env` 파일로 테스트
- **백업**: API 키를 안전한 곳에 백업
- **모니터링**: API 사용량을 주기적으로 확인

설정 완료 후에도 문제가 지속되면 API 키를 다시 생성해보세요!