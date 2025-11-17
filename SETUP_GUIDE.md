# Google Sheets 연동 설정 가이드

Streamlit Cloud에 배포할 때 Google Sheets를 데이터베이스로 사용하기 위한 설정 방법입니다.

## 1. Google Cloud 프로젝트 만들기

1. https://console.cloud.google.com 접속
2. 새 프로젝트 만들기 (또는 기존 프로젝트 선택)
3. 프로젝트 이름: `wallet-app` (또는 원하는 이름)

## 2. Google Sheets API 활성화

1. 좌측 메뉴에서 **API 및 서비스** → **라이브러리** 클릭
2. "Google Sheets API" 검색
3. **사용** 버튼 클릭
4. 같은 방법으로 "Google Drive API"도 활성화

## 3. 서비스 계정 만들기

1. 좌측 메뉴에서 **API 및 서비스** → **사용자 인증 정보** 클릭
2. **+ 사용자 인증 정보 만들기** → **서비스 계정** 선택
3. 서비스 계정 이름: `wallet-app-service` (또는 원하는 이름)
4. **만들기 및 계속** 클릭
5. 역할 선택: **편집자** 선택
6. **완료** 클릭

## 4. 서비스 계정 키 생성

1. 방금 만든 서비스 계정 클릭
2. **키** 탭으로 이동
3. **키 추가** → **새 키 만들기** 클릭
4. 키 유형: **JSON** 선택
5. **만들기** 클릭
6. JSON 파일이 자동으로 다운로드됩니다 (안전하게 보관!)

## 5. Google Sheets 스프레드시트 만들기

1. https://sheets.google.com 접속
2. 새 스프레드시트 만들기
3. 이름: "가계부" (또는 원하는 이름)
4. 스프레드시트 URL 복사 (예: `https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit`)

## 6. 스프레드시트 공유

1. 스프레드시트 우측 상단의 **공유** 버튼 클릭
2. 다운로드한 JSON 파일에서 `client_email` 값 복사
   - 예: `wallet-app-service@wallet-app-123456.iam.gserviceaccount.com`
3. 이 이메일 주소를 **편집자** 권한으로 추가
4. **완료** 클릭

## 7. Streamlit Cloud에 Secrets 설정

### 7-1. Streamlit Cloud 접속

1. https://share.streamlit.io 접속
2. 배포된 앱으로 이동
3. **Settings** (⚙️) → **Secrets** 클릭

### 7-2. Secrets 내용 작성

다운로드한 JSON 파일의 내용을 다음 형식으로 붙여넣기:

```toml
[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"

sheet_url = "YOUR_GOOGLE_SHEETS_URL"
```

**주의사항:**
- JSON 파일의 각 값을 위 형식의 해당 위치에 복사
- `private_key` 값에서 `\n`이 제대로 포함되어 있는지 확인
- `sheet_url`에는 스프레드시트 전체 URL 입력

### 7-3. 저장

**Save** 버튼 클릭하면 앱이 자동으로 재시작됩니다.

## 8. 완료!

이제 배포된 앱에서 데이터를 입력하면 Google Sheets에 저장됩니다.

스프레드시트를 직접 열어서 데이터를 확인하거나 수정할 수도 있습니다.

## 로컬 환경에서 테스트하기 (선택사항)

로컬에서도 Google Sheets를 사용하려면:

1. 프로젝트 폴더에 `.streamlit/secrets.toml` 파일 생성
2. 위와 동일한 내용 붙여넣기
3. `.gitignore`에 `.streamlit/secrets.toml` 추가되어 있는지 확인 (비밀 키가 GitHub에 올라가지 않도록!)

## 문제 해결

### "sheet_url이 설정되지 않았습니다" 오류

- Streamlit Secrets에 `sheet_url`이 제대로 설정되었는지 확인
- 스프레드시트 URL 전체를 복사했는지 확인

### "Permission denied" 오류

- 서비스 계정 이메일이 스프레드시트에 **편집자** 권한으로 공유되었는지 확인
- Google Sheets API와 Google Drive API가 모두 활성화되었는지 확인

### 데이터가 저장되지 않음

- Streamlit Cloud의 로그를 확인 (Settings → Logs)
- 스프레드시트 첫 번째 시트(Sheet1)를 사용하는지 확인
