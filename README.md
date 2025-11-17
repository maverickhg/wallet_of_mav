# 💰 가계부 앱

간단한 개인 가계부 관리 웹 애플리케이션입니다.

로컬 환경에서는 SQLite를, Streamlit Cloud 배포 시에는 Google Sheets를 데이터베이스로 사용합니다.

## 주요 기능

- **지출 추가**: 날짜, 항목, 금액, 지출처, 내용 입력
- **지출 내역 조회**: 전체/날짜 범위/카테고리별 필터링
- **지출 수정/삭제**: 기존 지출 내역 수정 및 삭제
- **통계**: 카테고리별/월별 지출 통계 및 시각화

## 카테고리

- 밥
- 커피
- 농구
- 사람(술 등)
- 기타

## 설치 방법

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

## 실행 방법

```bash
# 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 기술 스택

- **Frontend**: Streamlit
- **Database**: SQLite (로컬) / Google Sheets (배포)
- **Language**: Python 3.12+

## Streamlit Cloud 배포

### 1. GitHub에 푸시

```bash
git push origin main
```

### 2. Streamlit Cloud에 배포

1. https://share.streamlit.io 접속
2. **New app** 클릭
3. Repository 선택
4. Main file path: `app.py`
5. **Deploy** 클릭

### 3. Google Sheets 연동 설정

배포된 앱에서 데이터가 영구적으로 저장되도록 Google Sheets를 설정해야 합니다.

**상세한 설정 방법은 [SETUP_GUIDE.md](SETUP_GUIDE.md)를 참고하세요.**

간단 요약:
1. Google Cloud Console에서 서비스 계정 생성
2. Google Sheets API 활성화
3. 서비스 계정 JSON 키 다운로드
4. Google Sheets 스프레드시트 생성 및 서비스 계정에 공유
5. Streamlit Cloud Secrets에 자격 증명 추가

## 파일 구조

```
wallet_of_mav/
├── app.py              # Streamlit UI
├── database.py         # 데이터베이스 관리 (SQLite/Google Sheets)
├── requirements.txt    # 패키지 의존성
├── SETUP_GUIDE.md      # Google Sheets 연동 설정 가이드
├── README.md
└── wallet.db          # SQLite 데이터베이스 (로컬에서만, 자동 생성)
```

## 데이터 저장

- **로컬 환경**: 모든 지출 데이터는 `wallet.db` SQLite 파일에 저장됩니다.
- **Streamlit Cloud**: Google Sheets에 데이터가 저장됩니다. (영구 저장)

백업이 필요한 경우:
- 로컬: `wallet.db` 파일을 복사
- 배포: Google Sheets에서 스프레드시트 복사 또는 내보내기
