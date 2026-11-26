# 앱 실행 정보

프로젝트 루트의 `pyproject.toml`과 `uv.lock`으로 Python 3.12 및 Streamlit 의존성을 관리한다.
프로젝트 루트에서 `uv sync`를 실행한 뒤 다음 PowerShell 명령으로 앱을 시작한다.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + ';' + $env:PATH
python -m streamlit run app/streamlit_app.py
```

`app/streamlit_app.py`의 `PROJECT_ROOT`는 진입점 파일을 기준으로 프로젝트 루트를 가리킨다.
CSV 경로는 `PROJECT_ROOT / "data" / "산불발생통계(20251110).csv"`로 정의한다.

화면의 `시군 선택`에서 `모두 선택`을 고르면 강원 전체를 조회한다. `시군 1곳 선택`과
`시군 2곳 선택`을 고르면 해당 시군 입력이 나타난다.
