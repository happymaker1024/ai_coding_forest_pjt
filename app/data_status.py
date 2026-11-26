"""CSV 준비 결과와 중단 사유를 Streamlit 화면에 표시한다."""


def render_data_status(csv_path):
    """로드 실패 시 원인을 알리고 이후 화면 생성을 중단한다."""
    import streamlit as st

    from app.data_loader import DataLoadError, load_wildfire_data

    @st.cache_data(show_spinner="산불 기록을 불러오는 중...")
    def _load_cached(path):
        return load_wildfire_data(path)

    try:
        data = _load_cached(csv_path)
    except DataLoadError as exc:
        st.error(str(exc))
        st.stop()

    st.caption(
        f"✅ 데이터 준비 완료 · 전국 {len(data.nationwide):,}건 · "
        f"강원 {len(data.gangwon):,}건 · "
        f"전국 발생일 {data.first_date}~{data.last_date}"
    )
    return data
