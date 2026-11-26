"""집계 셀과 원본 상세 행의 일치를 확인한다."""

from pathlib import Path

from app.causes import cause_counts
from app.data_loader import load_wildfire_data
from app.details import detail_records
from app.filters import filter_records
from app.monthly import monthly_counts


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


def test_goseong_april_detail_matches_month_cell() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    detail = detail_records(selection, "고성", month=4)
    april_count = int(monthly_counts(selection).set_index("월").loc[4, "고성"])
    assert len(detail) == april_count == 1
    assert detail.iloc[0]["기타 원문"] == "차량화재"
    assert list(detail.columns) == ["발생일", "시군", "세부원인", "기타 원문"]


def test_goseong_other_detail_matches_cause_cell() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    detail = detail_records(selection, "고성", cause="기타(직접입력)")
    cause_count = int(
        cause_counts(selection).set_index("세부원인").loc["기타(직접입력)", "고성"]
    )
    assert len(detail) == cause_count == 2
    assert set(detail["기타 원문"]) == {"차량화재", "조사중"}
