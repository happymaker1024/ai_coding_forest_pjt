"""같은 조회 결과로 월별 건수 표와 비교 차트를 만든다."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.filters import FilterSelection


def region_totals(selection: FilterSelection) -> dict[str, int]:
    if not selection.cities:
        return {"강원 전체": len(selection.records)}
    counts = selection.records["발생장소_시군구"].value_counts()
    return {city: int(counts.get(city, 0)) for city in selection.cities}


def monthly_counts(selection: FilterSelection) -> pd.DataFrame:
    months = list(range(selection.start_month, selection.end_month + 1))
    table = pd.DataFrame({"월": months})
    for region in region_totals(selection):
        rows = selection.records
        if region != "강원 전체":
            rows = rows.loc[rows["발생장소_시군구"].eq(region)]
        counts = rows["발생일시_월"].value_counts()
        table[region] = [int(counts.get(month, 0)) for month in months]
    return table


def monthly_chart(table: pd.DataFrame) -> go.Figure:
    long = table.melt(id_vars="월", var_name="시군", value_name="기록 건수")
    chart = px.bar(long, x="월", y="기록 건수", color="시군", barmode="group")
    chart.update_xaxes(
        tickmode="array",
        tickvals=table["월"].tolist(),
        ticktext=[f"{month}월" for month in table["월"]],
    )
    chart.update_yaxes(rangemode="tozero", title_text="기록 건수")
    chart.update_layout(legend_title_text="시군", bargap=0.25)
    return chart
