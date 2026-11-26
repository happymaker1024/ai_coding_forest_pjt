"""강원 기록의 기간·시군 조회 조건."""

from dataclasses import dataclass

import pandas as pd


class FilterError(ValueError):
    """입력한 조회 조건이 유효하지 않을 때 표시할 오류."""


@dataclass(frozen=True)
class FilterSelection:
    start_year: int
    end_year: int
    start_month: int
    end_month: int
    cities: tuple[str, ...]
    records: pd.DataFrame


def city_options(gangwon: pd.DataFrame) -> tuple[str, ...]:
    """날짜 조건과 독립적인 전체 강원 시군 선택지."""
    return tuple(sorted(gangwon["발생장소_시군구"].dropna().unique()))


def filter_records(
    gangwon: pd.DataFrame,
    *,
    start_year: int,
    end_year: int,
    start_month: int,
    end_month: int,
    cities: tuple[str, ...] = (),
) -> FilterSelection:
    if start_year > end_year or start_month > end_month:
        raise FilterError("조회 기간을 바로잡아야 한다. 시작 값은 종료 값보다 늦을 수 없다.")
    if not (1 <= start_month <= 12 and 1 <= end_month <= 12):
        raise FilterError("조회 월은 1~12월 사이여야 한다.")
    if len(cities) != len(set(cities)):
        raise FilterError("시군은 서로 다른 곳을 선택해야 한다.")
    unknown = set(cities) - set(city_options(gangwon))
    if unknown:
        raise FilterError(f"강원 기록에 없는 시군이다: {', '.join(sorted(unknown))}")

    mask = (
        gangwon["발생일시_년"].between(start_year, end_year)
        & gangwon["발생일시_월"].between(start_month, end_month)
    )
    if cities:
        mask &= gangwon["발생장소_시군구"].isin(cities)

    return FilterSelection(
        start_year=start_year,
        end_year=end_year,
        start_month=start_month,
        end_month=end_month,
        cities=cities,
        records=gangwon.loc[mask].copy(),
    )
