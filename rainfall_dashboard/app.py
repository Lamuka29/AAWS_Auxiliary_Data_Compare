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
# FUNCTION - GET STATION NAME FROM FILE 1
# ============================================================

def get_station_name(
    uploaded_file,
    sheet_name
):

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=sheet_name,
        header=None,
        usecols="B",
        nrows=4
    )

    station_name = raw.iloc[3, 0]

    if pd.isna(station_name):
        return sheet_name

    return str(station_name).strip()

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

sheets1 = excel1.sheet_names
sheets2 = excel2.sheet_names


# ------------------------------------------------------------
# FILE 1
# Station name is stored in B4
# ------------------------------------------------------------

station_map1 = {}

for sheet in sheets1:

    try:

        station_name = get_station_name(
            file1,
            sheet
        )

        station_map1[station_name] = sheet

    except Exception:
        continue


# ------------------------------------------------------------
# FILE 2
# Station name = sheet name
# ------------------------------------------------------------

station_map2 = {
    sheet: sheet
    for sheet in sheets2
}


stations1 = list(
    station_map1.keys()
)

stations2 = list(
    station_map2.keys()
)
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
        station_map1[station1]
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
# ANALYSIS TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Monthly Comparison",
    "📈 Anomaly",
    "🥧 Rainfall Category",
    "📊 Histogram",
    "📅 Yearly Analysis"
])

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
# TAB 1 - MONTHLY COMPARISON
# ============================================================

with tab1:

    st.subheader(
        "📊 Monthly Rainfall Comparison"
    )

    fig, ax = plt.subplots(
        figsize=(15, 8)
    )

    x = np.arange(len(MONTHS))

    bar_width = 0.32

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

    ax.plot(
        x,
        target1.values,
        color="navy",
        marker="o",
        linewidth=2.5,
        label=f"{station1} {target_year}"
    )

    ax.plot(
        x,
        target2.values,
        color="crimson",
        marker="o",
        linewidth=2.5,
        label=f"{station2} {target_year}"
    )
    # ========================================================
    # TARGET YEAR VALUE LABELS
    # ========================================================
    
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
                    va="top",
                    fontsize=8
                )

    ax.set_title(
        f"{station1} vs {station2}\n"
        f"Mean Monthly Rainfall vs {target_year}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Month")

    ax.set_ylabel("Rainfall (mm)")

    ax.set_xticks(x)

    ax.set_xticklabels(MONTHS)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

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
# ANOMALY CALCULATION
# ============================================================

anomaly1 = (
    (target1 - mean1)
    / mean1.replace(0, np.nan)
) * 100

anomaly2 = (
    (target2 - mean2)
    / mean2.replace(0, np.nan)
) * 100

# ============================================================
# TAB 2 - ANOMALY
# ============================================================

with tab2:

    st.subheader(
        f"📊 Monthly Rainfall Anomaly - {target_year}"
    )

    # --------------------------------------------------------
    # ANOMALY BAR GRAPH
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    x = np.arange(
        len(MONTHS)
    )

    bar_width = 0.35

    # Station 1
    bar1 = ax.bar(
        x - bar_width / 2,
        anomaly1.values,
        width=bar_width,
        color="steelblue",
        edgecolor="black",
        label=station1
    )

    # Station 2
    bar2 = ax.bar(
        x + bar_width / 2,
        anomaly2.values,
        width=bar_width,
        color="darkorange",
        edgecolor="black",
        label=station2
    )

    # Zero line
    ax.axhline(
        0,
        color="black",
        linestyle="--",
        linewidth=1
    )

    # --------------------------------------------------------
    # BAR VALUE LABELS
    # --------------------------------------------------------

    for bars in [bar1, bar2]:

        for bar in bars:

            value = bar.get_height()

            if pd.notna(value):

                if value >= 0:
                    offset = 5
                    va = "bottom"
                else:
                    offset = -5
                    va = "top"

                ax.annotate(
                    f"{value:.1f}%",
                    (
                        bar.get_x()
                        + bar.get_width() / 2,
                        value
                    ),
                    xytext=(0, offset),
                    textcoords="offset points",
                    ha="center",
                    va=va,
                    fontsize=8
                )

    # --------------------------------------------------------
    # GRAPH SETTINGS
    # --------------------------------------------------------

    ax.set_title(
        f"Monthly Rainfall Anomaly - {target_year}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Anomaly (%)"
    )

    ax.set_xticks(
        x
    )

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
        loc="upper left",
        borderaxespad=0
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


    # ========================================================
    # ANOMALY TABLE
    # ========================================================

    st.subheader(
        "📋 Monthly Anomaly Table"
    )

    anomaly_table = pd.DataFrame({

        "Month":
            MONTHS,

        f"{station1} Anomaly (%)":
            anomaly1.values,

        f"{station2} Anomaly (%)":
            anomaly2.values,

        "Difference (%)":
            (
                anomaly1.values
                - anomaly2.values
            )

    })

    st.dataframe(
        anomaly_table.round(2),
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# TAB 3 - RAINFALL CATEGORY
# ============================================================

with tab3:

    st.subheader(
        f"🥧 Rainfall Category - {target_year}"
    )

    def rainfall_category(value):

        if pd.isna(value):
            return np.nan

        if value == 0:
            return "No Rain"

        elif value <= 10:
            return "Slight Rain"

        elif value <= 30:
            return "Moderate Rain"

        elif value <= 60:
            return "Heavy Rain"

        else:
            return "Very Heavy Rain"


    category1 = pd.Series(
        target1.values
    ).apply(
        rainfall_category
    )

    category2 = pd.Series(
        target2.values
    ).apply(
        rainfall_category
    )


    pie_categories = [
        "Slight Rain",
        "Moderate Rain",
        "Heavy Rain",
        "Very Heavy Rain"
    ]


    count1 = (
        category1
        .value_counts()
        .reindex(
            pie_categories,
            fill_value=0
        )
    )

    count2 = (
        category2
        .value_counts()
        .reindex(
            pie_categories,
            fill_value=0
        )
    )


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # STATION 1
    # --------------------------------------------------------

    with col1:

        fig1, ax1 = plt.subplots(
            figsize=(6, 6)
        )

        if count1.sum() > 0:

            ax1.pie(
                count1.values,
                labels=count1.index,
                autopct="%1.1f%%",
                startangle=90
            )

        ax1.set_title(
            station1
        )

        st.pyplot(
            fig1,
            use_container_width=True
        )

        plt.close(fig1)


    # --------------------------------------------------------
    # STATION 2
    # --------------------------------------------------------

    with col2:

        fig2, ax2 = plt.subplots(
            figsize=(6, 6)
        )

        if count2.sum() > 0:

            ax2.pie(
                count2.values,
                labels=count2.index,
                autopct="%1.1f%%",
                startangle=90
            )

        ax2.set_title(
            station2
        )

        st.pyplot(
            fig2,
            use_container_width=True
        )

        plt.close(fig2)
# ============================================================
# TAB 4 - HISTOGRAM
# ============================================================

with tab4:

    st.subheader(
        "📊 Slight & Moderate Rainfall Histogram"
    )

    values1 = (
        analysis1[MONTHS]
        .values
        .flatten()
    )

    values2 = (
        analysis2[MONTHS]
        .values
        .flatten()
    )

    values1 = values1[
        ~np.isnan(values1)
    ]

    values2 = values2[
        ~np.isnan(values2)
    ]


    # --------------------------------------------------------
    # SLIGHT + MODERATE ONLY
    # 0.1–30.0 mm
    # --------------------------------------------------------

    values1 = values1[
        (values1 > 0) &
        (values1 <= 30)
    ]

    values2 = values2[
        (values2 > 0) &
        (values2 <= 30)
    ]


    # --------------------------------------------------------
    # GRAPH
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(15, 8)
    )

    bins = np.arange(
        0,
        32,
        2
    )

    ax.hist(
        values1,
        bins=bins,
        alpha=0.6,
        edgecolor="black",
        label=station1
    )

    ax.hist(
        values2,
        bins=bins,
        alpha=0.6,
        edgecolor="black",
        label=station2
    )

    ax.set_title(
        "Distribution of Slight and Moderate Rainfall",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Rainfall (mm)"
    )

    ax.set_ylabel(
        "Frequency"
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)
# ============================================================
# TAB 5 - YEARLY ANALYSIS
# ============================================================

with tab5:

    st.subheader(
        "📅 Yearly Rainfall Analysis"
    )

    # --------------------------------------------------------
    # YEARLY DATA
    # --------------------------------------------------------

    yearly1 = (
        analysis1
        .set_index("YEAR")
        .reindex(common_years)
    )

    yearly2 = (
        analysis2
        .set_index("YEAR")
        .reindex(common_years)
    )

    # --------------------------------------------------------
    # YEARLY TOTAL
    # --------------------------------------------------------

    yearly_total1 = (
        yearly1[MONTHS]
        .sum(
            axis=1,
            skipna=True
        )
    )

    yearly_total2 = (
        yearly2[MONTHS]
        .sum(
            axis=1,
            skipna=True
        )
    )

    # --------------------------------------------------------
    # YEARLY MEAN
    # --------------------------------------------------------

    yearly_mean1 = (
        yearly1[MONTHS]
        .mean(
            axis=1,
            skipna=True
        )
    )

    yearly_mean2 = (
        yearly2[MONTHS]
        .mean(
            axis=1,
            skipna=True
        )
    )

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    yearly_table = pd.DataFrame({

        "Year":
            common_years,

        f"{station1} Total (mm)":
            yearly_total1.values,

        f"{station2} Total (mm)":
            yearly_total2.values,

        "Total Difference (mm)":
            (
                yearly_total1.values
                -
                yearly_total2.values
            ),

        f"{station1} Mean (mm)":
            yearly_mean1.values,

        f"{station2} Mean (mm)":
            yearly_mean2.values,

        "Mean Difference (mm)":
            (
                yearly_mean1.values
                -
                yearly_mean2.values
            )

    })

    st.dataframe(
        yearly_table.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # YEARLY TOTAL GRAPH
    # ========================================================

    st.subheader(
        "📊 Yearly Total Rainfall"
    )

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    x = np.arange(
        len(common_years)
    )

    bar_width = 0.35

    bar1 = ax.bar(
        x - bar_width / 2,
        yearly_total1.values,
        width=bar_width,
        color="steelblue",
        edgecolor="black",
        label=station1
    )

    bar2 = ax.bar(
        x + bar_width / 2,
        yearly_total2.values,
        width=bar_width,
        color="darkorange",
        edgecolor="black",
        label=station2
    )

    # --------------------------------------------------------
    # VALUE LABELS
    # --------------------------------------------------------

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

    ax.set_title(
        "Yearly Total Rainfall",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Year")

    ax.set_ylabel(
        "Total Rainfall (mm)"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        common_years
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)

    # ========================================================
    # YEARLY MEAN GRAPH
    # ========================================================

    st.subheader(
        "📈 Yearly Mean Monthly Rainfall"
    )

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    ax.plot(
        common_years,
        yearly_mean1.values,
        marker="o",
        linewidth=2.5,
        label=station1
    )

    ax.plot(
        common_years,
        yearly_mean2.values,
        marker="o",
        linewidth=2.5,
        label=station2
    )

    ax.set_title(
        "Yearly Mean Monthly Rainfall",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Year")

    ax.set_ylabel(
        "Mean Rainfall (mm)"
    )

    ax.set_xticks(
        common_years
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)
