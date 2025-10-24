# 🔐 GitHub 배포 보안 가이드

## ✅ 완료된 보안 설정

### 1. API 키 보안화
- `app_new.py`: 하드코딩된 API 키 → 환경변수로 변경
- `app.py`: 이미 환경변수 사용 중

### 2. 생성된 파일들
- `.env`: 로컬 개발용 환경변수 (git에서 제외됨)
- `.env.example`: 설정 예시 파일 (git에 포함)
- `.gitignore`: 민감한 파일들 자동 제외

### 3. 보안 검증
✅ API 키가 환경변수에서 정상 로드됨
✅ 앱이 환경변수로 정상 실행됨
✅ .env 파일이 git에서 제외됨

## 🚀 GitHub 업로드 절차

### 1. 현재 상태 확인
```bash
git status
# .env 파일이 나타나지 않아야 함 (정상)
```

### 2. 안전한 커밋
```bash
git add .
git commit -m "🔐 보안: API 키를 환경변수로 변경"
git push origin main
```

### 3. 협업자/사용자 안내
- `.env.example` 파일을 참고하여 개인 `.env` 파일 생성
- OpenWeather API 키를 발급받아 환경변수에 설정

## 🌐 배포 플랫폼별 설정

### Streamlit Cloud
1. GitHub 저장소 연결
2. **Advanced settings** → **Secrets** 에서:
   ```
   OPENWEATHER_API_KEY = "your_actual_api_key"
   ```

### Heroku
1. 환경변수 설정:
   ```bash
   heroku config:set OPENWEATHER_API_KEY=your_actual_api_key
   ```

### Railway/Render
1. 대시보드에서 Environment Variables 설정:
   - Key: `OPENWEATHER_API_KEY`
   - Value: `your_actual_api_key`

## ⚡ 빠른 테스트

로컬에서 보안이 적용된 앱 실행:
```bash
streamlit run app_new.py
```

브라우저에서 http://localhost:8501 접속하여 정상 작동 확인

## 🔒 보안 체크리스트

- [x] 하드코딩된 API 키 제거
- [x] 환경변수 사용
- [x] .env 파일 git 제외
- [x] .env.example 예시 제공
- [x] README 배포 가이드 업데이트
- [x] 앱 정상 작동 검증

✅ **GitHub 배포 준비 완료!**