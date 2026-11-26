"""원본 세부원인 집계와 0건 분모를 확인한다."""

from pathlib import Path

from app.causes import cause_chart, cause_counts, other_share, other_share_table
from app.data_loader import load_wildfire_data
from app.filters import filter_records
from app.monthly import region_totals


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


def test_all_gangwon_other_share() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2022,
        end_year=2025,
        start_month=1,
        end_month=12,
    )
    table = cause_counts(selection)
    assert region_totals(selection) == {"강원 전체": 218}
    assert int(table.loc[table["세부원인"].eq("기타(직접입력)"), "강원 전체"].iloc[0]) == 172
    assert int(table["강원 전체"].sum()) == 218
    assert other_share(selection) == {"강원 전체": (172, "78.9%")}


def test_two_city_causes_sum_to_region_totals() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    table = cause_counts(selection)
    indexed = table.set_index("세부원인")
    assert int(indexed.loc["기타(직접입력)", "고성"]) == 2
    assert int(indexed.loc["낙뢰", "고성"]) == 1
    assert int(indexed.loc["기타(직접입력)", "강릉"]) == 6
    assert indexed.sum().to_dict() == region_totals(selection)
    assert other_share(selection) == {
        "고성": (2, "66.7%"),
        "강릉": (6, "66.7%"),
    }
    share_table = other_share_table(selection)
    assert share_table.columns.tolist() == ["시군", "기타(직접입력) 건수", "비중"]
    assert share_table.set_index("시군").loc["고성"].tolist() == [2, "66.7%"]
    assert share_table.set_index("시군").loc["강릉"].tolist() == [6, "66.7%"]

    chart = cause_chart(table)
    assert chart.layout.barmode == "group"
    assert [list(trace.x) for trace in chart.data] == [
        indexed["고성"].tolist(),
        indexed["강릉"].tolist(),
    ]


def test_zero_result_has_dash_share() -> None:
    data = load_wildfire_data(SOURCE)
    selection = filter_records(
        data.gangwon,
        start_year=2023,
        end_year=2023,
        start_month=3,
        end_month=5,
        cities=("양양",),
    )
    assert cause_counts(selection).to_dict("list") == {
        "세부원인": ["기타(직접입력)"],
        "양양": [0],
    }
    assert other_share(selection) == {"양양": (0, "–")}
