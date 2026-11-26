"""현재 필터 수치와 출처를 사용한 복사 문장을 확인한다."""

from pathlib import Path

import pandas as pd

from app.data_loader import load_wildfire_data
from app.filters import FilterSelection, filter_records
from app.summary import make_summary


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


def test_two_city_summary_has_exact_figures_and_source() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    summary = make_summary(selection, SOURCE.name)
    for value in (
        "2022~2025년 각 연도 3~5월",
        "고성 기록 3건, 최다 기록 월 3월 2건, 기타(직접입력) 2건",
        "강릉 기록 9건, 최다 기록 월 4월 5건, 기타(직접입력) 6건",
        SOURCE.name,
    ):
        assert value in summary


def test_zero_summary_has_condition_and_source() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2023,
        end_year=2023,
        start_month=3,
        end_month=5,
        cities=("양양",),
    )
    summary = make_summary(selection, SOURCE.name)
    assert "2023년 3~5월" in summary
    assert "양양" in summary
    assert "선택 조건의 기록 0건" in summary
    assert SOURCE.name in summary


def test_tied_peak_lists_every_peak_month() -> None:
    records = pd.DataFrame(
        {
            "발생장소_시군구": ["고성", "고성"],
            "발생일시_월": [3, 4],
            "발생원인_세부원인": ["낙뢰", "기타(직접입력)"],
        }
    )
    selection = FilterSelection(2024, 2024, 3, 5, ("고성",), records)
    summary = make_summary(selection, "test.csv")
    assert "최다 기록 월 3월, 4월 1건" in summary
    assert "기타(직접입력) 1건" in summary
