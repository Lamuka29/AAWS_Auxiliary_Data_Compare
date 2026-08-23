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
    Perbandingan data hujan bulanan antara **dua fail**
    bagi stesen dan tahun yang sama.
    """
)


# ============================================================
# FUNCTION - FILE 1
# ============================================================

def read_file1(
    uploaded_file,
    station
):

    # --------------------------------------------------------
    # FILE 1
    #
    # Sheet = Station
    # A = YEAR
    # B:M = JAN:DEC
    # N = ANNUAL
    #
    # Table starts around row 9/10
    # Header = row 10
    # Data = row 11
    # --------------------------------------------------------

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=station,
        header=None,
        usecols="A:N"
    )

    # Data starts row 11
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

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

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

    data["YEAR"] = (
        data["YEAR"]
        .astype(int)
    )

    # --------------------------------------------------------
    # MONTHS
    # --------------------------------------------------------

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    # --------------------------------------------------------
    # ANNUAL
    # --------------------------------------------------------

    data["ANNUAL"] = pd.to_numeric(
        data["ANNUAL"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
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
# FUNCTION - FILE 2
# ============================================================

def read_file2(
    uploaded_file,
    station
):

    # --------------------------------------------------------
    # FILE 2
    #
    # Sheet = Station
    # B = YEAR
    # C:N = JAN:DEC
    # O = ANNUAL
    #
    # Table starts around B5:O5/6
    # Header = row 6
    # Data = row 7
    # --------------------------------------------------------

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=station,
        header=None,
        usecols="B:O"
    )

    # Data starts row 7
    data = raw.iloc[6:].copy()

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
    # YEAR
    # --------------------------------------------------------

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

    data["YEAR"] = (
        data["YEAR"]
        .astype(int)
    )

    # --------------------------------------------------------
    # MONTHS
    # --------------------------------------------------------

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    # --------------------------------------------------------
    # ANNUAL
    # --------------------------------------------------------

    data["ANNUAL"] = pd.to_numeric(
        data["ANNUAL"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
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
# UPLOAD FILES
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
        "File 2 - Monthly/Yearly Rainfall",
        type=["xlsx", "xls"],
        key="file2"
    )


if file1 is None or file2 is None:

    st.info(
        "⬆️ Sila upload kedua-dua fail."
    )

    st.stop()


# ============================================================
# READ EXCEL
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
# STATION LIST
# ============================================================

stations1 = excel1.sheet_names

stations2 = excel2.sheet_names


if not stations1:

    st.error(
        "❌ Tiada stesen dalam File 1."
    )

    st.stop()


if not stations2:

    st.error(
        "❌ Tiada stesen dalam File 2."
    )

    st.stop()


# ============================================================
# SELECT STATION
# ============================================================

col1, col2 = st.columns(2)

with col1:

    station1 = st.selectbox(
        "📍 File 1 - Station",
        stations1,
        key="station1"
    )

with col2:

    station2 = st.selectbox(
        "📍 File 2 - Station",
        stations2,
        key="station2"
    )


# ============================================================
# READ SELECTED STATIONS
# ============================================================

try:

    data1 = read_file1(
        file1,
        station1
    )

    data2 = read_file2(
        file2,
        station2
    )

except Exception as e:

    st.error(
        f"❌ Gagal membaca fail: {e}"
    )

    st.stop()


# ============================================================
# COMMON YEARS
# ============================================================

years1 = set(
    data1["YEAR"]
)

years2 = set(
    data2["YEAR"]
)

common_years = sorted(
    years1.intersection(years2)
)


if not common_years:

    st.error(
        "❌ Tiada tahun yang sama "
        "antara kedua-dua stesen."
    )

    st.stop()


# ============================================================
# INFORMATION
# ============================================================

st.success(
    f"📍 File 1: {station1} | "
    f"File 2: {station2} | "
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
# FILTER COMMON YEARS
# ============================================================

analysis1 = data1[
    data1["YEAR"].isin(
        common_years
    )
].copy()

analysis2 = data2[
    data2["YEAR"].isin(
        common_years
    )
].copy()


# ============================================================
# MEAN MONTHLY RAINFALL
# ============================================================

mean1 = (
    analysis1[MONTHS]
    .mean(
        axis=0,
        skipna=True
    )
    .reindex(MONTHS)
)

mean2 = (
    analysis2[MONTHS]
    .mean(
        axis=0,
        skipna=True
    )
    .reindex(MONTHS)
)


# ============================================================
# TARGET YEAR
# ============================================================

target1 = (
    analysis1[
        analysis1["YEAR"]
        == target_year
    ]
    .iloc[0][MONTHS]
    .reindex(MONTHS)
)

target2 = (
    analysis2[
        analysis2["YEAR"]
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


# ------------------------------------------------------------
# MEAN
# ------------------------------------------------------------

bar1 = ax.bar(
    x - bar_width / 2,
    mean1.values,
    width=bar_width,
    color="steelblue",
    edgecolor="black",
    label=f"{station1} Mean"
)

bar2 = ax.bar(
    x + bar_width / 2,
    mean2.values,
    width=bar_width,
    color="darkorange",
    edgecolor="black",
    label=f"{station2} Mean"
)


# ------------------------------------------------------------
# TARGET YEAR
# ------------------------------------------------------------

ax.plot(
    x,
    target1.values,
    color="navy",
    marker="o",
    linewidth=2.5,
    markersize=7,
    label=f"{station1} {target_year}"
)

ax.plot(
    x,
    target2.values,
    color="crimson",
    marker="o",
    linewidth=2.5,
    markersize=7,
    label=f"{station2} {target_year}"
)


# ============================================================
# BAR LABELS
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
# LINE LABELS
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
    f"Monthly Rainfall Comparison\n"
    f"{station1} vs {station2}",
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

    f"{station1} Mean (mm)":
        mean1.values,

    f"{station2} Mean (mm)":
        mean2.values,

    "Mean Difference (mm)":
        mean_difference.values,

    f"{station1} {target_year} (mm)":
        target1.values,

    f"{station2} {target_year} (mm)":
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

annual_comparison = pd.DataFrame({

    "Year":
        common_years,

    f"{station1} Annual (mm)":
        analysis1
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
        .values,

    f"{station2} Annual (mm)":
        analysis2
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
        .values

})


annual_comparison[
    "Difference (mm)"
] = (
    annual_comparison[
        f"{station1} Annual (mm)"
    ]
    -
    annual_comparison[
        f"{station2} Annual (mm)"
    ]
)


st.dataframe(
    annual_comparison.round(2),
    use_container_width=True,
    hide_index=True
)
