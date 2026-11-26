"""원본 세부원인별 건수와 기타 비중."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.filters import FilterSelection
from app.monthly import region_totals


OTHER_CAUSE = "기타(직접입력)"
CAUSE_COLUMN = "발생원인_세부원인"


def cause_counts(selection: FilterSelection) -> pd.DataFrame:
    causes = set(selection.records[CAUSE_COLUMN].dropna().unique())
    causes.add(OTHER_CAUSE)
    regions = list(region_totals(selection))
    counts_by_region = {}
    for region in regions:
        rows = selection.records
        if region != "강원 전체":
            rows = rows.loc[rows["발생장소_시군구"].eq(region)]
        counts_by_region[region] = rows[CAUSE_COLUMN].value_counts()

    def total(cause: str) -> int:
        return sum(int(counts_by_region[region].get(cause, 0)) for region in regions)

    ordered = sorted(causes, key=lambda cause: (-total(cause), cause))
    table = pd.DataFrame({"세부원인": ordered})
    for region in regions:
        table[region] = [int(counts_by_region[region].get(cause, 0)) for cause in ordered]
    return table


def cause_chart(table: pd.DataFrame) -> go.Figure:
    long = table.melt(id_vars="세부원인", var_name="시군", value_name="건수")
    long["표시값"] = long["건수"].apply(lambda value: f"{value:,}" if value else "")
    chart = px.bar(
        long,
        x="건수",
        y="세부원인",
        color="시군",
        barmode="group",
        orientation="h",
        text="표시값",
    )
    chart.update_yaxes(
        categoryorder="array",
        categoryarray=list(reversed(table["세부원인"].tolist())),
        title_text="세부원인",
    )
    chart.update_xaxes(rangemode="tozero", title_text="건수")
    chart.update_traces(textposition="outside", cliponaxis=False)
    chart.update_layout(
        legend_title_text="시군",
        bargap=0.12,
        bargroupgap=0.05,
        height=max(320, 72 * len(table)),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return chart


def other_share(selection: FilterSelection) -> dict[str, tuple[int, str]]:
    result = {}
    for region, total in region_totals(selection).items():
        rows = selection.records
        if region != "강원 전체":
            rows = rows.loc[rows["발생장소_시군구"].eq(region)]
        other = int(rows[CAUSE_COLUMN].eq(OTHER_CAUSE).sum())
        percentage = f"{other / total * 100:.1f}%" if total else "–"
        result[region] = (other, percentage)
    return result


def other_share_table(selection: FilterSelection) -> pd.DataFrame:
    rows = [
        {"시군": region, "기타(직접입력) 건수": other_count, "비중": share}
        for region, (other_count, share) in other_share(selection).items()
    ]
    return pd.DataFrame(rows, columns=["시군", "기타(직접입력) 건수", "비중"])
