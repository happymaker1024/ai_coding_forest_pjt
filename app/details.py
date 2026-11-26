"""집계 조건에 해당하는 원본 행을 상세 표로 변환한다."""

import pandas as pd

from app.causes import CAUSE_COLUMN, OTHER_CAUSE
from app.filters import FilterSelection


DETAIL_COLUMNS = ("발생일", "시군", "세부원인", "기타 원문")


def detail_causes(selection: FilterSelection, city: str) -> tuple[str, ...]:
    rows = selection.records.loc[selection.records["발생장소_시군구"].eq(city)]
    causes = set(rows[CAUSE_COLUMN].dropna().unique())
    causes.add(OTHER_CAUSE)
    return (OTHER_CAUSE, *sorted(causes - {OTHER_CAUSE}))


def detail_records(
    selection: FilterSelection,
    city: str,
    *,
    month: int | None = None,
    cause: str | None = None,
) -> pd.DataFrame:
    if (month is None) == (cause is None):
        raise ValueError("월 또는 세부원인 중 한 기준을 선택해야 한다.")
    if selection.cities and city not in selection.cities:
        raise ValueError("현재 선택한 시군이 아니다.")

    rows = selection.records.loc[selection.records["발생장소_시군구"].eq(city)]
    if month is not None:
        rows = rows.loc[rows["발생일시_월"].eq(month)]
    else:
        rows = rows.loc[rows[CAUSE_COLUMN].eq(cause)]

    dates = pd.to_datetime(
        {
            "year": rows["발생일시_년"],
            "month": rows["발생일시_월"],
            "day": rows["발생일시_일"],
        }
    )
    return pd.DataFrame(
        {
            "발생일": dates.dt.strftime("%Y-%m-%d").to_numpy(),
            "시군": rows["발생장소_시군구"].to_numpy(),
            "세부원인": rows[CAUSE_COLUMN].to_numpy(),
            "기타 원문": rows["발생원인_기타"].fillna("").to_numpy(),
        },
        columns=DETAIL_COLUMNS,
    )
