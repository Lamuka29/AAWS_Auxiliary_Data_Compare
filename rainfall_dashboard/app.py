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
# TITLE
# ============================================================

st.title("🌧️ Monthly Rainfall File Comparison")

st.markdown(
    """
    Aplikasi ini membandingkan **dua fail data hujan bulanan**
    bagi tahun yang sama.

    **File 1 vs File 2**
    - Mean Monthly Rainfall
    - Target Year Monthly Rainfall
    - Difference antara kedua-dua fail
    """
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
# FUNCTION - READ FILE
# ============================================================

def read_rainfall_file(uploaded_file):

    raw = pd.read_excel(
        uploaded_file,
        header=None
    )

    # --------------------------------------------------------
    # FIND HEADER ROW
    # --------------------------------------------------------

    header_row = None

    for i in range(min(15, len(raw))):

        values = (
            raw.iloc[i]
            .astype(str)
            .str.strip()
            .str.upper()
            .tolist()
        )

        if "YEAR" in values:

            header_row = i
            break

    if header_row is None:

        raise ValueError(
            "Column 'YEAR' tidak dijumpai."
        )

    # --------------------------------------------------------
    # READ DATA
    # --------------------------------------------------------

    data = pd.read_excel(
        uploaded_file,
        header=header_row
    )

    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    data.columns = [
        str(col)
        .strip()
        .upper()
        for col in data.columns
    ]

    # --------------------------------------------------------
    # CHECK YEAR
    # --------------------------------------------------------

    if "YEAR" not in data.columns:

        raise ValueError(
            "Column 'YEAR' tidak dijumpai."
        )

    # --------------------------------------------------------
    # ADD MISSING MONTH COLUMNS
    # --------------------------------------------------------

    for month in MONTHS:

        if month not in data.columns:

            data[month] = np.nan

    # --------------------------------------------------------
    # ADD ANNUAL IF MISSING
    # --------------------------------------------------------

    if "ANNUAL" not in data.columns:

        data["ANNUAL"] = np.nan

    # --------------------------------------------------------
    # KEEP REQUIRED COLUMNS
    # --------------------------------------------------------

    data = data[
        ["YEAR"] + MONTHS + ["ANNUAL"]
    ].copy()

    # --------------------------------------------------------
    # CLEAN YEAR
    # --------------------------------------------------------

    data["YEAR"] = pd.to_numeric(
        data["YEAR"],
        errors="coerce"
    )

    # Remove rows such as "Average"

    data = data[
        data["YEAR"].notna()
    ].copy()

    data["YEAR"] = (
        data["YEAR"]
        .astype(int)
    )

    # --------------------------------------------------------
    # CLEAN MONTHS
    # --------------------------------------------------------

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    # --------------------------------------------------------
    # CLEAN ANNUAL
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

st.subheader("📁 Upload Rainfall Files")

col1, col2 = st.columns(2)

with col1:

    file1 = st.file_uploader(
        "File 1",
        type=["xlsx", "xls"],
        key="file1"
    )

with col2:

    file2 = st.file_uploader(
        "File 2",
        type=["xlsx", "xls"],
        key="file2"
    )


# ============================================================
# PROCESS FILES
# ============================================================

if file1 is None or file2 is None:

    st.info(
        "⬆️ Sila upload kedua-dua fail untuk memulakan analisis."
    )

    st.stop()


# ============================================================
# READ FILES
# ============================================================

try:

    data1 = read_rainfall_file(
        file1
    )

    data2 = read_rainfall_file(
        file2
    )

except Exception as e:

    st.error(
        f"❌ Gagal membaca fail: {e}"
    )

    st.stop()


# ============================================================
# FIND COMMON YEARS
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
        "❌ Tiada tahun yang sama antara File 1 dan File 2."
    )

    st.stop()


# ============================================================
# FILE INFORMATION
# ============================================================

st.success(
    f"✅ Tahun yang sama: "
    f"{common_years[0]}–{common_years[-1]}"
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
    data1["YEAR"].isin(common_years)
].copy()

analysis2 = data2[
    data2["YEAR"].isin(common_years)
].copy()


# ============================================================
# MEAN MONTHLY RAINFALL
# ============================================================

mean1 = (
    analysis1[MONTHS]
    .mean(axis=0)
    .reindex(MONTHS)
)

mean2 = (
    analysis2[MONTHS]
    .mean(axis=0)
    .reindex(MONTHS)
)


# ============================================================
# TARGET YEAR DATA
# ============================================================

target1 = (
    data1[
        data1["YEAR"] == target_year
    ]
    .iloc[0][MONTHS]
    .reindex(MONTHS)
)

target2 = (
    data2[
        data2["YEAR"] == target_year
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

st.subheader("📌 Analysis Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Analysis Period",
        f"{common_years[0]}–{common_years[-1]}"
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

for bars in [bar1, bar2]:

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

    for i, value in enumerate(values):

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
    f"Mean vs Target Year {target_year}",
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
# COMPARISON TABLE
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

annual_comparison = pd.DataFrame({

    "Year":
        common_years,

    "File 1 Annual (mm)":
        analysis1
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
        .values,

    "File 2 Annual (mm)":
        analysis2
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
        .values

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
