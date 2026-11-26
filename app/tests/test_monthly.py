"""월별 표의 0 채움과 공통 축 비교를 확인한다."""

from pathlib import Path

from app.data_loader import load_wildfire_data
from app.filters import filter_records
from app.monthly import monthly_chart, monthly_counts, region_totals


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


def test_two_city_monthly_table_and_chart() -> None:
    gangwon = load_wildfire_data(SOURCE).gangwon
    selection = filter_records(
        gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    table = monthly_counts(selection)
    assert region_totals(selection) == {"고성": 3, "강릉": 9}
    assert table.to_dict("list") == {
        "월": [3, 4, 5],
        "고성": [2, 1, 0],
        "강릉": [3, 5, 1],
    }
    chart = monthly_chart(table)
    assert chart.layout.barmode == "group"
    assert all(trace.yaxis in (None, "y") for trace in chart.data)
    assert [list(trace.y) for trace in chart.data] == [[2, 1, 0], [3, 5, 1]]


def test_empty_city_still_has_zero_months() -> None:
    gangwon = load_wildfire_data(SOURCE).gangwon
    selection = filter_records(
        gangwon,
        start_year=2023,
        end_year=2023,
        start_month=3,
        end_month=5,
        cities=("양양",),
    )
    assert region_totals(selection) == {"양양": 0}
    assert monthly_counts(selection).to_dict("list") == {
        "월": [3, 4, 5],
        "양양": [0, 0, 0],
    }
