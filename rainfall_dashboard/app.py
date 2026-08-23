# ============================================================
# MONTHLY RAINFALL FILE COMPARISON
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Monthly Rainfall Comparison",
    page_icon="🌧️",
    layout="wide"
)


# ============================================================
# CONSTANT
# ============================================================

MONTHS = [
    "JAN", "FEB", "MAR", "APR",
    "MAY", "JUN", "JUL", "AUG",
    "SEP", "OCT", "NOV", "DEC"
]


# ============================================================
# TITLE
# ============================================================

st.title(
    "🌧️ Monthly Rainfall File Comparison"
)

st.markdown(
    """
    Aplikasi ini membandingkan **dua fail data hujan bulanan**
    bagi stesen dan tahun yang sama.

    **File 1 vs File 2**
    - Mean Monthly Rainfall
    - Target Year Monthly Rainfall
    - Difference antara kedua-dua fail
    """
)


# ============================================================
# FUNCTION - READ FILE 1
# ============================================================

def read_file1(
    uploaded_file,
    year
):

    # --------------------------------------------------------
    # FILE 1 STRUCTURE
    #
    # A = YEAR
    # B:M = JAN:DEC
    # N = ANNUAL
    #
    # Header = row 10
    # Data = row 11 onwards
    # --------------------------------------------------------

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=str(year),
        header=None,
        usecols="A:N"
    )

    # --------------------------------------------------------
    # DATA STARTS ROW 11
    # Python index = 10
    # --------------------------------------------------------

    data = raw.iloc[10:].copy()

    # --------------------------------------------------------
    # SET COLUMN NAMES
    # --------------------------------------------------------

    data.columns = [
        "YEAR",
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
        "ANNUAL"
    ]

    # --------------------------------------------------------
    # CONVERT NUMERIC
    # --------------------------------------------------------

    for column in [
        "YEAR",
        *MONTHS,
        "ANNUAL"
    ]:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # KEEP VALID YEAR
    # --------------------------------------------------------

    data = data[
        data["YEAR"].notna()
    ].copy()

    data = data[
        data["YEAR"].between(
            1900,
            2100
        )
    ].copy()

    data["YEAR"] = (
        data["YEAR"]
        .astype(int)
    )

    # --------------------------------------------------------
    # FILE 1 SHEET REPRESENTS ONE YEAR
    #
    # Calculate monthly total from daily data
    # --------------------------------------------------------

    monthly_total = (
        data[MONTHS]
        .sum(
            axis=0,
            skipna=True
        )
        .reindex(MONTHS)
    )

    annual_total = (
        monthly_total.sum()
    )

    return {
        "YEAR": year,
        "MONTHLY": monthly_total,
        "ANNUAL": annual_total
    }


# ============================================================
# FUNCTION - READ FILE 2
# ============================================================

def read_file2(
    uploaded_file,
    station
):

    # --------------------------------------------------------
    # FILE 2 STRUCTURE
    #
    # B = YEAR
    # C:N = JAN:DEC
    # O = ANNUAL
    #
    # Header = row 6
    # Data = row 7 onwards
    # --------------------------------------------------------

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=station,
        header=None,
        usecols="B:O"
    )

    # --------------------------------------------------------
    # DATA STARTS ROW 7
    # Python index = 6
    # --------------------------------------------------------

    data = raw.iloc[6:].copy()

    # --------------------------------------------------------
    # SET COLUMN NAMES
    # --------------------------------------------------------

    data.columns = [
        "YEAR",
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
        "ANNUAL"
    ]

    # --------------------------------------------------------
    # CONVERT YEAR
    # --------------------------------------------------------

    data["YEAR"] = pd.to_numeric(
        data["YEAR"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # REMOVE NON-YEAR ROWS
    #
    # This automatically removes:
    # Average
    # blank rows
    # headers
    # --------------------------------------------------------

    data = data[
        data["YEAR"].notna()
    ].copy()

    data = data[
        data["YEAR"].between(
            1900,
            2100
        )
    ].copy()

    data["YEAR"] = (
        data["YEAR"]
        .astype(int)
    )

    # --------------------------------------------------------
    # CONVERT MONTHS
    # --------------------------------------------------------

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    # --------------------------------------------------------
    # CONVERT ANNUAL
    # --------------------------------------------------------

    data["ANNUAL"] = pd.to_numeric(
        data["ANNUAL"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATE YEARS
    # --------------------------------------------------------

    data = (
        data
        .drop_duplicates(
            subset="YEAR",
            keep="first"
        )
        .sort_values("YEAR")
        .reset_index(drop=True)
    )

    return data


# ============================================================
# FILE UPLOAD
# ============================================================

st.subheader(
    "📁 Upload Rainfall Files"
)

col1, col2 = st.columns(2)

with col1:

    file1 = st.file_uploader(
        "File 1 - Daily Rainfall",
        type=["xlsx", "xls"],
        key="file1"
    )

with col2:

    file2 = st.file_uploader(
        "File 2 - Monthly Rainfall",
        type=["xlsx", "xls"],
        key="file2"
    )


# ============================================================
# CHECK FILES
# ============================================================

if file1 is None or file2 is None:

    st.info(
        "⬆️ Sila upload kedua-dua fail "
        "untuk memulakan analisis."
    )

    st.stop()


# ============================================================
# READ EXCEL FILES
# ============================================================

try:

    excel1 = pd.ExcelFile(file1)

    excel2 = pd.ExcelFile(file2)

except Exception as e:

    st.error(
        f"❌ Gagal membaca fail: {e}"
    )

    st.stop()


# ============================================================
# GET YEARS FROM FILE 1
# ============================================================

file1_years = []

for sheet in excel1.sheet_names:

    try:

        year = int(
            str(sheet).strip()
        )

        if 1900 <= year <= 2100:

            file1_years.append(year)

    except:

        continue


file1_years = sorted(
    set(file1_years)
)


if not file1_years:

    st.error(
        "❌ Tiada sheet tahun dijumpai "
        "dalam File 1."
    )

    st.stop()


# ============================================================
# GET STATIONS FROM FILE 2
# ============================================================

file2_stations = (
    excel2.sheet_names
)


if not file2_stations:

    st.error(
        "❌ Tiada sheet stesen dijumpai "
        "dalam File 2."
    )

    st.stop()


# ============================================================
# SELECT STATION
# ============================================================

station = st.selectbox(
    "📍 Select Station",
    file2_stations,
    key="station"
)


# ============================================================
# READ FILE 2
# ============================================================

try:

    data2 = read_file2(
        file2,
        station
    )

except Exception as e:

    st.error(
        f"❌ Gagal membaca File 2: {e}"
    )

    st.stop()


# ============================================================
# GET YEARS FROM FILE 2
# ============================================================

file2_years = sorted(
    data2["YEAR"]
    .unique()
)


# ============================================================
# COMMON YEARS
# ============================================================

common_years = sorted(
    set(file1_years)
    .intersection(file2_years)
)


if not common_years:

    st.error(
        "❌ Tiada tahun yang sama "
        "antara File 1 dan File 2."
    )

    st.stop()


# ============================================================
# INFORMATION
# ============================================================

st.success(
    f"📍 Station: {station} | "
    f"Years: {common_years[0]}–"
    f"{common_years[-1]}"
)


# ============================================================
# TARGET YEAR
# ============================================================

target_year = st.selectbox(
    "🎯 Select Target Year",
    common_years,
    index=len(common_years) - 1
)


# ============================================================
# READ FILE 1 - ALL SHEETS
# ============================================================

file1_data = {}


for sheet in excel1.sheet_names:

    try:

        raw = pd.read_excel(
            file1,
            sheet_name=sheet,
            header=None,
            usecols="A:N"
        )

        # ----------------------------------------------------
        # DATA STARTS ROW 11
        # ----------------------------------------------------

        data = raw.iloc[10:].copy()

        data.columns = [
            "YEAR",
            "JAN",
            "FEB",
            "MAR",
            "APR",
            "MAY",
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV",
            "DEC",
            "ANNUAL"
        ]

        # ----------------------------------------------------
        # CONVERT YEAR
        # ----------------------------------------------------

        data["YEAR"] = pd.to_numeric(
            data["YEAR"],
            errors="coerce"
        )

        data = data[
            data["YEAR"].notna()
        ].copy()

        data = data[
            data["YEAR"].between(
                1900,
                2100
            )
        ].copy()

        if data.empty:
            continue

        data["YEAR"] = (
            data["YEAR"]
            .astype(int)
        )

        # ----------------------------------------------------
        # CONVERT MONTHS
        # ----------------------------------------------------

        for month in MONTHS:

            data[month] = pd.to_numeric(
                data[month],
                errors="coerce"
            )

        # ----------------------------------------------------
        # MONTHLY TOTAL
        # ----------------------------------------------------

        monthly_total = (
            data[MONTHS]
            .sum(
                axis=0,
                skipna=True
            )
            .reindex(MONTHS)
        )

        year = int(
            data["YEAR"].iloc[0]
        )

        file1_data[year] = {
            "MONTHLY": monthly_total,
            "ANNUAL": monthly_total.sum(),
            "SHEET": sheet
        }

    except Exception:
        continue


# ============================================================
# CHECK FILE 1
# ============================================================

file1_years = sorted(
    file1_data.keys()
)


if not file1_years:

    st.error(
        "❌ Tiada data YEAR dijumpai dalam File 1."
    )

    st.stop()


# ============================================================
# CREATE FILE 1 TABLE
# ============================================================

file1_table = pd.DataFrame(
    {
        year:
        file1_results[year]["MONTHLY"]
        for year in file1_results
    }
).T


file1_table.index.name = "YEAR"


# ============================================================
# FILE 1 MEAN
# ============================================================

mean1 = (
    file1_table[MONTHS]
    .mean(
        axis=0,
        skipna=True
    )
    .reindex(MONTHS)
)


# ============================================================
# FILE 2 ANALYSIS
# ============================================================

analysis2 = data2[
    data2["YEAR"].isin(
        common_years
    )
].copy()


# ============================================================
# FILE 2 MEAN
# ============================================================

mean2 = (
    analysis2[MONTHS]
    .mean(
        axis=0,
        skipna=True
    )
    .reindex(MONTHS)
)


# ============================================================
# TARGET YEAR - FILE 1
# ============================================================

target1 = (
    file1_table
    .loc[
        target_year,
        MONTHS
    ]
    .reindex(MONTHS)
)


# ============================================================
# TARGET YEAR - FILE 2
# ============================================================

target2 = (
    data2[
        data2["YEAR"]
        == target_year
    ]
    .iloc[0][MONTHS]
    .reindex(MONTHS)
)


# ============================================================
# DIFFERENCE
# ============================================================

mean_difference = (
    mean1 - mean2
)


target_difference = (
    target1 - target2
)


# ============================================================
# SUMMARY
# ============================================================

st.subheader(
    "📌 Analysis Summary"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Analysis Period",
        f"{common_years[0]}–"
        f"{common_years[-1]}"
    )

with col2:

    st.metric(
        "Target Year",
        target_year
    )

with col3:

    st.metric(
        "Number of Years",
        len(common_years)
    )


# ============================================================
# GRAPH
# ============================================================

st.subheader(
    "📊 Monthly Rainfall Comparison"
)

fig, ax = plt.subplots(
    figsize=(15, 8)
)

x = np.arange(
    len(MONTHS)
)

bar_width = 0.32


# ============================================================
# MEAN BARS
# ============================================================

bar1 = ax.bar(
    x - bar_width / 2,
    mean1.values,
    width=bar_width,
    color="steelblue",
    edgecolor="black",
    label="File 1 Mean"
)

bar2 = ax.bar(
    x + bar_width / 2,
    mean2.values,
    width=bar_width,
    color="darkorange",
    edgecolor="black",
    label="File 2 Mean"
)


# ============================================================
# TARGET YEAR LINES
# ============================================================

ax.plot(
    x,
    target1.values,
    color="navy",
    marker="o",
    linewidth=2.5,
    markersize=7,
    label=f"File 1 {target_year}"
)

ax.plot(
    x,
    target2.values,
    color="crimson",
    marker="o",
    linewidth=2.5,
    markersize=7,
    label=f"File 2 {target_year}"
)


# ============================================================
# BAR VALUE LABELS
# ============================================================

for bars in [
    bar1,
    bar2
]:

    for bar in bars:

        value = bar.get_height()

        if pd.notna(value):

            ax.annotate(
                f"{value:.1f}",
                (
                    bar.get_x()
                    + bar.get_width() / 2,
                    value
                ),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8
            )


# ============================================================
# LINE VALUE LABELS
# ============================================================

for values in [
    target1.values,
    target2.values
]:

    for i, value in enumerate(
        values
    ):

        if pd.notna(value):

            ax.annotate(
                f"{value:.1f}",
                (
                    x[i],
                    value
                ),
                xytext=(0, -15),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )


# ============================================================
# GRAPH SETTINGS
# ============================================================

ax.set_title(
    f"{station}\n"
    f"Mean Monthly Rainfall vs "
    f"Target Year {target_year}",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel(
    "Month",
    fontsize=12
)

ax.set_ylabel(
    "Rainfall (mm)",
    fontsize=12
)

ax.set_xticks(x)

ax.set_xticklabels(
    MONTHS
)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)

ax.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# MONTHLY COMPARISON TABLE
# ============================================================

st.subheader(
    "📋 Monthly Comparison"
)

comparison = pd.DataFrame({

    "Month":
        MONTHS,

    "File 1 Mean (mm)":
        mean1.values,

    "File 2 Mean (mm)":
        mean2.values,

    "Mean Difference (mm)":
        mean_difference.values,

    f"File 1 {target_year} (mm)":
        target1.values,

    f"File 2 {target_year} (mm)":
        target2.values,

    "Target Difference (mm)":
        target_difference.values

})


st.dataframe(
    comparison.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANNUAL COMPARISON
# ============================================================

st.subheader(
    "📊 Annual Rainfall Comparison"
)

annual1 = []

for year in common_years:

    annual1.append(
        file1_results[year]["ANNUAL"]
    )


annual2 = (
    analysis2
    .set_index("YEAR")
    .reindex(common_years)["ANNUAL"]
    .values
)


annual_comparison = pd.DataFrame({

    "Year":
        common_years,

    "File 1 Annual (mm)":
        annual1,

    "File 2 Annual (mm)":
        annual2

})


annual_comparison[
    "Difference (mm)"
] = (
    annual_comparison[
        "File 1 Annual (mm)"
    ]
    -
    annual_comparison[
        "File 2 Annual (mm)"
    ]
)


st.dataframe(
    annual_comparison.round(2),
    use_container_width=True,
    hide_index=True
)
