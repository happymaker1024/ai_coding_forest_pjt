"""원본 산불 기록을 읽고 분석에 필요한 기본 범위를 검증한다."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = (
    "발생일시_년",
    "발생일시_월",
    "발생일시_일",
    "발생장소_시도",
    "발생장소_시군구",
    "발생원인_세부원인",
    "발생원인_기타",
)


class DataLoadError(Exception):
    """데이터 준비를 계속할 수 없을 때 표시할 오류."""


@dataclass(frozen=True)
class WildfireData:
    nationwide: pd.DataFrame
    gangwon: pd.DataFrame
    first_date: date
    last_date: date


def load_wildfire_data(csv_path: Path) -> WildfireData:
    """CP949 CSV를 원본 행 단위로 읽고 강원 기록을 선택한다."""
    try:
        nationwide = pd.read_csv(csv_path, encoding="cp949")
    except FileNotFoundError as exc:
        raise DataLoadError(f"데이터 파일을 찾을 수 없다: {csv_path}") from exc
    except UnicodeError as exc:
        raise DataLoadError(f"CSV를 CP949로 해독할 수 없다: {csv_path}") from exc
    except pd.errors.ParserError as exc:
        raise DataLoadError(f"CSV 형식을 읽을 수 없다: {csv_path}") from exc

    missing = [column for column in REQUIRED_COLUMNS if column not in nationwide.columns]
    if missing:
        raise DataLoadError(f"필수 열이 누락되었다: {', '.join(missing)}")

    try:
        dates = pd.to_datetime(
            {
                "year": nationwide["발생일시_년"],
                "month": nationwide["발생일시_월"],
                "day": nationwide["발생일시_일"],
            },
            errors="raise",
        )
    except (ValueError, TypeError) as exc:
        raise DataLoadError("발생일을 해석할 수 없다. 연·월·일 값을 확인해야 한다.") from exc

    nationwide["발생장소_시도"] = nationwide["발생장소_시도"].str.strip()
    nationwide["발생장소_시군구"] = nationwide["발생장소_시군구"].str.strip()
    gangwon = nationwide.loc[nationwide["발생장소_시도"].eq("강원")].copy()

    return WildfireData(
        nationwide=nationwide,
        gangwon=gangwon,
        first_date=dates.min().date(),
        last_date=dates.max().date(),
    )
