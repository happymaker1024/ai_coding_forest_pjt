"""강원 산불 예방 브리핑의 Streamlit 진입점."""

from pathlib import Path

import streamlit as st

from app.data_status import render_data_status
from app.causes import cause_chart, cause_counts, other_share_table
from app.details import detail_causes, detail_records
from app.filters import FilterError, city_options, filter_records
from app.monthly import monthly_chart, monthly_counts, region_totals
from app.summary import make_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "산불발생통계(20251110).csv"

st.set_page_config(page_title="강원 산불 예방 브리핑", page_icon="🔥", layout="wide")

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: #FBF1E7;
        border: 1px solid rgba(226, 87, 43, 0.22);
        border-left: 4px solid #E2572B;
        border-radius: 10px;
        padding: 0.7rem 1rem 0.55rem 1rem;
    }
    div[data-testid="stMetricLabel"] p {
        color: #9A4A1F;
        font-weight: 600;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p {
        color: #B8401A;
        font-weight: 700;
    }
    hr {
        border-top: 1px solid rgba(47, 82, 51, 0.25);
    }
    </style>
    <div style="
        padding: 1.1rem 1.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #2F5233 0%, #1C3A21 55%, #201511 100%);
        margin-bottom: 0.9rem;
        box-shadow: 0 6px 18px rgba(28, 58, 33, 0.25);
    ">
        <div style="font-size:0.78rem; letter-spacing:0.16em; text-transform:uppercase; color:#F2B880;">
            Gangwon Wildfire Watch
        </div>
        <div style="font-size:1.85rem; font-weight:800; color:#FFF4E8; margin-top:0.15rem;">
            🔥 강원 산불 예방 브리핑
        </div>
        <div style="color:#D9CBB9; font-size:0.92rem; margin-top:0.2rem;">
            데이터로 보는 산불 발생 현황, 한눈에 비교하고 공유한다
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

data = render_data_status(DATA_PATH)
st.caption(f"📄 출처: {DATA_PATH.name} · 전국 기록 범위: {data.first_date}~{data.last_date}")

years = sorted(data.nationwide["발생일시_년"].unique())

with st.sidebar:
    st.header("📅 조회 조건")
    st.caption("기간과 시군을 선택하면 아래 결과가 함께 바뀐다.")

    st.subheader("🗓️ 기간")
    left_year, right_year = st.columns(2)
    start_year = left_year.selectbox(
        "시작 연도", years, index=0, key="start_year", help="조회를 시작할 연도다."
    )
    end_year = right_year.selectbox(
        "종료 연도",
        years,
        index=len(years) - 1,
        key="end_year",
        help="조회를 마칠 연도다. 시작 연도보다 늦어야 한다.",
    )
    left_month, right_month = st.columns(2)
    start_month = left_month.selectbox(
        "시작 월", range(1, 13), index=2, key="start_month", help="연도별로 같은 월 구간을 비교한다."
    )
    end_month = right_month.selectbox(
        "종료 월",
        range(1, 13),
        index=4,
        key="end_month",
        help="시작 월보다 늦어야 한다. 예: 3~5월은 봄철 구간이다.",
    )

    st.divider()
    st.subheader("📍 시군")
    available_cities = city_options(data.gangwon)
    selected_cities = tuple(
        st.multiselect(
            "시군 선택",
            available_cities,
            key="selected_cities",
            help="선택하지 않으면 강원 전체를 조회한다. 여러 시군을 자유롭게 선택해 비교할 수 있다.",
        )
    )

try:
    selection = filter_records(
        data.gangwon,
        start_year=start_year,
        end_year=end_year,
        start_month=start_month,
        end_month=end_month,
        cities=selected_cities,
    )
except FilterError as exc:
    st.error(str(exc))
    st.stop()

with st.container(border=True):
    st.metric("선택 조건의 기록", f"{len(selection.records):,}건")
    if selection.records.empty:
        st.info("선택 조건의 기록 0건")

    if selection.cities:
        city_totals = list(region_totals(selection).items())
        for row_start in range(0, len(city_totals), 6):
            row_items = city_totals[row_start : row_start + 6]
            row_columns = st.columns(len(row_items))
            for column, (city, count) in zip(row_columns, row_items):
                column.metric(f"{city} 기록", f"{count:,}건")

tab_monthly, tab_causes, tab_detail, tab_summary = st.tabs(
    ["🗓️ 월별 비교", "🔥 세부원인 비교", "📄 원본 확인", "📋 요약 복사"]
)

with tab_monthly:
    st.subheader("🗓️ 월별 건수 비교")
    month_table = monthly_counts(selection)
    st.plotly_chart(monthly_chart(month_table), width="stretch")
    st.dataframe(month_table, hide_index=True, width="stretch")

with tab_causes:
    cause_table = cause_counts(selection)
    st.subheader("🔥 세부원인별 비교")
    st.caption("건수가 많은 세부원인부터 차례로 보여준다. 막대 끝 숫자는 건수다.")
    st.plotly_chart(cause_chart(cause_table), width="stretch")

    st.divider()
    st.subheader("📝 기타(직접입력) 비중")
    st.caption("해당 조건의 총건수 중 ‘기타(직접입력)’가 차지하는 비중이다.")
    st.dataframe(other_share_table(selection), hide_index=True, width="stretch")

    st.divider()
    st.caption("세부원인별 건수 표 (건수 많은 순)")
    st.dataframe(cause_table, hide_index=True, width="stretch")

with tab_detail:
    st.subheader("🔍 원본 상세 조회")
    detail_cities = selection.cities or city_options(data.gangwon)
    col_city, col_mode = st.columns(2)
    detail_city = col_city.selectbox("상세 시군", detail_cities, key="detail_city")
    detail_mode = col_mode.radio("상세 조회 기준", ("월", "세부원인"), horizontal=True)
    if detail_mode == "월":
        detail_month = st.selectbox(
            "상세 월", range(selection.start_month, selection.end_month + 1)
        )
        details = detail_records(selection, detail_city, month=detail_month)
    else:
        detail_cause = st.selectbox("상세 세부원인", detail_causes(selection, detail_city))
        details = detail_records(selection, detail_city, cause=detail_cause)

    st.caption(f"상세 기록 {len(details):,}건")
    st.dataframe(details, hide_index=True, width="stretch")
    st.download_button(
        "⬇️ 상세 기록 CSV 다운로드",
        details.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"상세기록_{detail_city}.csv",
        mime="text/csv",
        disabled=details.empty,
    )

with tab_summary:
    st.subheader("📋 회의용 요약")
    summary = make_summary(selection, DATA_PATH.name)
    st.caption("아래 문장의 복사 아이콘을 눌러 회의 자료에 붙여 넣을 수 있다.")
    st.code(summary, language=None, wrap_lines=True)
