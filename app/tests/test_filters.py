"""기간 경계와 날짜에 독립적인 시군 선택을 확인한다."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.data_loader import load_wildfire_data
from app.filters import FilterError, city_options, filter_records


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


@pytest.fixture(scope="module")
def gangwon():
    return load_wildfire_data(SOURCE).gangwon


def test_initial_and_two_city_counts(gangwon) -> None:
    initial = filter_records(
        gangwon, start_year=2022, end_year=2025, start_month=3, end_month=5
    )
    assert len(initial.records) == 119
    pair = filter_records(
        gangwon,
        start_year=2022,
        end_year=2025,
        start_month=3,
        end_month=5,
        cities=("고성", "강릉"),
    )
    assert pair.records["발생장소_시군구"].value_counts().to_dict() == {
        "강릉": 9,
        "고성": 3,
    }


def test_empty_result_does_not_remove_city_option(gangwon) -> None:
    empty = filter_records(
        gangwon,
        start_year=2023,
        end_year=2023,
        start_month=3,
        end_month=5,
        cities=("양양",),
    )
    assert empty.records.empty
    assert len(city_options(gangwon)) == 17
    assert "양양" in city_options(gangwon)


@pytest.mark.parametrize(
    "years, months",
    [((2025, 2022), (3, 5)), ((2022, 2025), (5, 3))],
)
def test_reversed_period_stops_filtering(gangwon, years, months) -> None:
    with pytest.raises(FilterError, match="조회 기간을 바로잡아야 한다"):
        filter_records(
            gangwon,
            start_year=years[0],
            end_year=years[1],
            start_month=months[0],
            end_month=months[1],
        )


def test_filter_controls_keep_city_and_stop_invalid_summary() -> None:
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "streamlit_app.py").run()

    def by_label(widgets, label):
        return next(widget for widget in widgets if widget.label == label)

    assert not app.exception
    city_select = by_label(app.multiselect, "시군 선택")
    assert city_select.value == []
    assert "Select all" not in city_select.options
    assert app.metric[0].value == "119건"
    assert "산불발생통계(20251110).csv" in app.caption[1].value

    by_label(app.multiselect, "시군 선택").set_value(["고성"])
    app.run()
    assert app.metric[0].value == "3건"

    by_label(app.multiselect, "시군 선택").set_value(["고성", "강릉"])
    app.run()
    assert app.metric[0].value == "12건"
    assert {metric.label: metric.value for metric in app.metric}["고성 기록"] == "3건"
    assert {metric.label: metric.value for metric in app.metric}["강릉 기록"] == "9건"

    by_label(app.multiselect, "시군 선택").set_value([])
    app.run()
    assert app.metric[0].value == "119건"
    assert "강원 전체" in app.code[0].value
    assert not any(metric.label == "고성 기록" for metric in app.metric)

    by_label(app.selectbox, "시작 월").set_value(1)
    by_label(app.selectbox, "종료 월").set_value(12)
    app.run()
    assert app.metric[0].value == "218건"
    assert "강원 전체 기록 218건" in app.code[0].value
    by_label(app.selectbox, "시작 월").set_value(3)
    by_label(app.selectbox, "종료 월").set_value(5)
    app.run()

    by_label(app.selectbox, "시작 연도").set_value(2023)
    by_label(app.selectbox, "종료 연도").set_value(2023)
    by_label(app.multiselect, "시군 선택").set_value(["양양"])
    app.run()
    city_select = by_label(app.multiselect, "시군 선택")
    assert city_select.value == ["양양"]
    assert "양양" in city_select.options
    assert app.metric[0].value == "0건"
    assert app.info[0].value == "선택 조건의 기록 0건"

    by_label(app.selectbox, "시작 월").set_value(5)
    by_label(app.selectbox, "종료 월").set_value(3)
    app.run()
    assert len(app.error) == 1
    assert "조회 기간을 바로잡아야 한다" in app.error[0].value
    assert not app.metric
