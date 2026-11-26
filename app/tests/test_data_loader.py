"""CSV 준비 단계의 정상값과 집계 중단 조건을 확인한다."""

import hashlib
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from app.data_loader import DataLoadError, load_wildfire_data
from app.data_status import render_data_status


SOURCE = Path(__file__).resolve().parents[2] / "data" / "산불발생통계(20251110).csv"


def test_source_counts_dates_and_read_only() -> None:
    before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    raw = pd.read_csv(SOURCE, encoding="cp949")
    data = load_wildfire_data(SOURCE)
    after = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

    assert before == after
    assert data.nationwide.shape == (2020, 18)
    assert len(data.gangwon) == 218
    assert data.gangwon["발생장소_시군구"].nunique() == 17
    assert data.gangwon["발생장소_시군구"].eq("강릉").sum() == 25
    assert (raw["발생장소_시군구"].str.strip().eq("강릉") & raw["발생장소_시군구"].ne("강릉")).sum() == 3
    assert data.first_date.isoformat() == "2022-01-01"
    assert data.last_date.isoformat() == "2025-09-11"


def test_missing_file_stops_loading(tmp_path: Path) -> None:
    with pytest.raises(DataLoadError, match="데이터 파일을 찾을 수 없다"):
        load_wildfire_data(tmp_path / "missing.csv")


def test_decoding_error_stops_loading(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad_encoding.csv"
    bad_csv.write_bytes(b"\xff")
    with pytest.raises(DataLoadError, match="CP949로 해독할 수 없다"):
        load_wildfire_data(bad_csv)


def test_missing_columns_stops_loading(tmp_path: Path) -> None:
    bad_csv = tmp_path / "missing_columns.csv"
    bad_csv.write_bytes("발생일시_년\n2025\n".encode("cp949"))
    with pytest.raises(DataLoadError, match="필수 열이 누락되었다") as caught:
        load_wildfire_data(bad_csv)
    assert "발생원인_기타" in str(caught.value)


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("missing", "데이터 파일을 찾을 수 없다"),
        ("decoding", "CP949로 해독할 수 없다"),
        ("columns", "필수 열이 누락되었다"),
    ],
)
def test_error_is_visible_and_stops_output(
    tmp_path: Path, case: str, expected: str
) -> None:
    csv_path = tmp_path / f"{case}.csv"
    if case == "decoding":
        csv_path.write_bytes(b"\xff")
    elif case == "columns":
        csv_path.write_bytes("발생일시_년\n2025\n".encode("cp949"))

    app = AppTest.from_function(render_data_status, args=(csv_path,)).run()
    assert not app.exception
    assert len(app.error) == 1
    assert expected in app.error[0].value
    assert not app.caption
