# 강원 산불 예방 브리핑

강원특별자치도 시군 산불 예방 담당자가 같은 기간의 산불 발생 기록을 시군별로 비교하고,
집계 수치를 원본 행까지 추적해 회의 자료용 요약을 바로 가져갈 수 있도록 돕는 Streamlit 대시보드입니다.

자세한 서비스 기획은 [docs/SERVICE_PLAN.md](docs/SERVICE_PLAN.md)를 참고하세요.

## 주요 기능

- 연도·월 범위·시군(최대 2곳) 조건으로 조회하는 대시보드 상단 필터
- 시군별 총건수와 월별 발생 건수 비교 차트
- 세부원인별 건수 비교와 '기타(직접입력)' 비중 표시
- 월 또는 원인을 선택하면 해당 원본 기록(발생일, 시군, 세부원인, 기타 원문)을 표로 확인
- 조회 조건과 집계 수치를 회의 자료용 문장으로 바로 복사

## 기술 스택

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (패키지/가상환경 관리)
- Streamlit, pandas, plotly
- pytest (테스트)

## 사전 준비물

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## 설치 및 실행 (Windows / PowerShell 기준)

1. 저장소를 내려받습니다.

   ```powershell
   git clone https://github.com/happymaker1024/ai_coding_forest_pjt.git
   cd ai_coding_forest_pjt
   ```

2. 프로젝트 루트에서 의존성을 설치합니다.

   ```powershell
   uv sync
   ```

3. Streamlit 앱을 실행합니다.

   ```powershell
   uv run streamlit run app/streamlit_app.py
   ```

4. 터미널에 출력되는 로컬 주소(기본값 `http://localhost:8501`)를 브라우저에서 엽니다.

> macOS/Linux 환경이라면 명령어는 동일하게 동작합니다.

## 테스트 실행

```powershell
uv run pytest app/tests -v
```

## 프로젝트 구조

```
.
├── app/                # Streamlit 앱 소스코드
│   ├── streamlit_app.py    # 앱 진입점
│   └── tests/               # pytest 테스트 코드
├── data/               # 원본 산불 발생 통계 데이터(CSV)
├── docs/               # 서비스 기획, 개발 환경 설정 등 문서
├── tasks/              # 개발 명세(PRD, 작업 목록)
├── report/             # 검증 결과 및 스크린샷
├── pyproject.toml      # 의존성 정의
└── uv.lock             # 의존성 잠금 파일
```

## 데이터 출처

- 입력 파일: `data/산불발생통계(20251110).csv` (CP949, 전국 2,020행)
- 원본 출처: [공공데이터포털 산림청 산불통계데이터](https://www.data.go.kr/data/15121380/fileData.do)

데이터 집계 기준과 범위에 대한 자세한 내용은 [docs/SERVICE_PLAN.md](docs/SERVICE_PLAN.md)의
"데이터 확인과 집계 기준" 항목을 참고하세요.
