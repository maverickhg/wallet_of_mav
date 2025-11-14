# 💰 가계부 앱

간단한 개인 가계부 관리 웹 애플리케이션입니다. Streamlit과 SQLite를 사용하여 만들어졌습니다.

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
- **Database**: SQLite
- **Language**: Python 3.12+

## 파일 구조

```
wallet_of_mav/
├── app.py              # Streamlit UI
├── database.py         # SQLite 데이터베이스 관리
├── requirements.txt    # 패키지 의존성
├── wallet.db          # SQLite 데이터베이스 (자동 생성)
└── README.md
```

## 데이터 저장

모든 지출 데이터는 `wallet.db` SQLite 파일에 저장됩니다.
백업이 필요한 경우 이 파일을 복사하면 됩니다.
