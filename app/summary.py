"""회의 자료에 붙여 넣을 통계 요약 문장."""

from app.causes import other_share
from app.filters import FilterSelection
from app.monthly import monthly_counts, region_totals


def make_summary(selection: FilterSelection, filename: str) -> str:
    year_range = (
        f"{selection.start_year}년"
        if selection.start_year == selection.end_year
        else f"{selection.start_year}~{selection.end_year}년 각 연도"
    )
    month_range = (
        f"{selection.start_month}월"
        if selection.start_month == selection.end_month
        else f"{selection.start_month}~{selection.end_month}월"
    )
    regions = ", ".join(selection.cities) if selection.cities else "강원 전체"
    condition = f"조회 기간 {year_range} {month_range}; 조회 시군 {regions}"
    source = f"출처 {filename}"

    if selection.records.empty:
        return f"{condition}. 선택 조건의 기록 0건. {source}."

    monthly = monthly_counts(selection).set_index("월")
    other = other_share(selection)
    sentences = []
    for region, total in region_totals(selection).items():
        monthly_values = monthly[region]
        peak_count = int(monthly_values.max())
        if peak_count:
            peak_months = ", ".join(
                f"{month}월" for month in monthly_values.index[monthly_values.eq(peak_count)]
            )
            peak_text = f"최다 기록 월 {peak_months} {peak_count}건"
        else:
            peak_text = "최다 기록 월 없음"
        other_count = other[region][0]
        sentences.append(
            f"{region} 기록 {total}건, {peak_text}, 기타(직접입력) {other_count}건"
        )
    return f"{condition}. {'; '.join(sentences)}. {source}."
