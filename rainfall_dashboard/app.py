import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io


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
# DOWNLOAD FUNCTIONS
# ============================================================

def download_plot(fig, filename, key):

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    buffer.seek(0)

    st.download_button(
        "⬇️ Download Graph",
        data=buffer,
        file_name=filename,
        mime="image/png",
        key=key
    )


def download_table(df, filename, key):

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Table",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=key
    )


# ============================================================
# FUNCTION - GET STATION NAME
# ============================================================

def get_station_name(uploaded_file, sheet_name):

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=sheet_name,
        header=None,
        usecols="B",
        nrows=4
    )

    station_name = raw.iloc[3, 0]

    if pd.isna(station_name):
        return str(sheet_name)

    return str(station_name).strip()


# ============================================================
# FUNCTION - FILE 1
# ============================================================

def read_file1(uploaded_file, station):

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=station,
        header=None,
        usecols="A:N"
    )

    data = raw.iloc[10:].copy()

    data.columns = [
        "YEAR",
        *MONTHS,
        "ANNUAL"
    ]

    data["YEAR"] = pd.to_numeric(
        data["YEAR"],
        errors="coerce"
    )

    data = data[
        data["YEAR"].between(
            1900,
            2100
        )
    ].copy()

    data["YEAR"] = data["YEAR"].astype(int)

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    data["ANNUAL"] = pd.to_numeric(
        data["ANNUAL"],
        errors="coerce"
    )

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

def read_file2(uploaded_file, station):

    raw = pd.read_excel(
        uploaded_file,
        sheet_name=station,
        header=None,
        usecols="B:O"
    )

    data = raw.iloc[6:].copy()

    data.columns = [
        "YEAR",
        *MONTHS,
        "ANNUAL"
    ]

    data["YEAR"] = pd.to_numeric(
        data["YEAR"],
        errors="coerce"
    )

    data = data[
        data["YEAR"].between(
            1900,
            2100
        )
    ].copy()

    data["YEAR"] = data["YEAR"].astype(int)

    for month in MONTHS:

        data[month] = pd.to_numeric(
            data[month],
            errors="coerce"
        )

    data["ANNUAL"] = pd.to_numeric(
        data["ANNUAL"],
        errors="coerce"
    )

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
# TITLE
# ============================================================

st.title(
    "🌧️ Monthly Rainfall File Comparison"
)

st.markdown(
    """
    Perbandingan data hujan tahunan antara
    **Data AAWS** dan **Data Kajiiklim**
    bagi tahun yang sama.
    """
)


# ============================================================
# UPLOAD FILES
# ============================================================

st.subheader("📁 Upload Rainfall Data Files")

col1, col2 = st.columns(2)

with col1:

    file1 = st.file_uploader(
        "File 1 - Data AAWS MyMetData",
        type=["xlsx", "xls"],
        key="file1"
    )

with col2:

    file2 = st.file_uploader(
        "File 2 - Data Auksiliari Kajiiklim",
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

sheets1 = [
    sheet
    for sheet in excel1.sheet_names
    if not str(sheet).strip().endswith(".1")
]

sheets2 = excel2.sheet_names


# ============================================================
# FILE 1 - STATION MAP
# ============================================================

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


# ============================================================
# FILE 2 - STATION MAP
# ============================================================

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


if not stations1:

    st.error(
        "❌ Tiada stesen dijumpai dalam File 1."
    )

    st.stop()


if not stations2:

    st.error(
        "❌ Tiada stesen dijumpai dalam File 2."
    )

    st.stop()


# ============================================================
# SELECT STATION
# ============================================================
# PENTING:
# HANYA ADA SATU station1 DAN SATU station2
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
        station_map2[station2]
    )

except Exception as e:

    st.error(
        f"❌ Gagal membaca fail: {e}"
    )

    st.stop()


# ============================================================
# ANALYSIS DATA
# ============================================================

analysis1 = data1.copy()
analysis2 = data2.copy()
print("analysis1")

# ============================================================
# COMMON YEARS
# ============================================================

years1 = set(
    analysis1["YEAR"]
)

years2 = set(
    analysis2["YEAR"]
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
    index=len(common_years) - 1,
    key="target_year"
)


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
        analysis1["YEAR"] == target_year
    ]
    .iloc[0][MONTHS]
    .reindex(MONTHS)
)

target2 = (
    analysis2[
        analysis2["YEAR"] == target_year
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
# ERROR ANALYSIS
# ============================================================

basic_diff = (
    target1 - target2
)

percentage_diff = (
    basic_diff
    / target2.replace(0, np.nan)
) * 100

absolute_error = (
    basic_diff.abs()
)

mae = absolute_error.mean(
    skipna=True
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Monthly Comparison",
    "📈 Anomaly",
    "📊 Histogram",
    "📅 Yearly Comparison",
    "📏 Error Analysis",
    "📦 Boxplot",
    "🔥 Heatmap"
])
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
mean_difference = (mean1 - mean2)
target_difference = (target1 - target2)
# ============================================================
# ERROR ANALYSIS CALCULATION
# File 1 = Automatic Station
# File 2 = Observation
# ============================================================
# Basic Difference
basic_diff = (target1 - target2)
# Percentage Difference
percentage_diff = (basic_diff / target2.replace(0, np.nan)) * 100
# Absolute Error
absolute_error = (basic_diff.abs())
# Mean Absolute Error
mae = (absolute_error.mean(skipna=True))

# ============================================================
# TAB 1 - MONTHLY COMPARISON
# ============================================================
with tab1:
    st.subheader("📊 Monthly Rainfall Comparison")

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
    download_plot(
        fig,
        f"monthly_comparison_{station1}_{station2}_{target_year}.png",
        "download_monthly_comparison_graph"
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
    download_table(
        comparison,
        f"monthly_comparison_{station1}_{station2}_{target_year}.csv",
        "download_monthly_comparison_table"
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
    download_plot(
        fig,
        f"rainfall_anomaly_{station1}_{station2}_{target_year}.png",
        "download_anomaly_graph"
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
    download_table(
        anomaly_table.round(2),
        f"rainfall_anomaly_{station1}_{station2}_{target_year}.csv",
        "download_anomaly_table"
    )
# ============================================================
# TAB 3 - HISTOGRAM
# ============================================================

with tab3:

    st.subheader(
        "📊 Rainfall Data Distribution by Category"
    )

    # --------------------------------------------------------
    # GET ALL RAINFALL VALUES
    # --------------------------------------------------------

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

    # Remove NaN
    values1 = values1[
        ~np.isnan(values1)
    ]

    values2 = values2[
        ~np.isnan(values2)
    ]

    # --------------------------------------------------------
    # CATEGORY FUNCTION
    # --------------------------------------------------------

    def rainfall_category(value):

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


    # --------------------------------------------------------
    # CLASSIFY DATA
    # --------------------------------------------------------

    categories1 = pd.Series(
        values1
    ).apply(
        rainfall_category
    )

    categories2 = pd.Series(
        values2
    ).apply(
        rainfall_category
    )

    # --------------------------------------------------------
    # CATEGORY ORDER
    # --------------------------------------------------------

    rainfall_categories = [
        "No Rain",
        "Slight Rain",
        "Moderate Rain",
        "Heavy Rain",
        "Very Heavy Rain"
    ]

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    count1 = (
        categories1
        .value_counts()
        .reindex(
            rainfall_categories,
            fill_value=0
        )
    )

    count2 = (
        categories2
        .value_counts()
        .reindex(
            rainfall_categories,
            fill_value=0
        )
    )

    # ========================================================
    # HISTOGRAM / CATEGORY FREQUENCY
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(15, 8)
    )

    x = np.arange(
        len(rainfall_categories)
    )

    bar_width = 0.35

    bar1 = ax.bar(
        x - bar_width / 2,
        count1.values,
        width=bar_width,
        color="steelblue",
        edgecolor="black",
        label=station1
    )

    bar2 = ax.bar(
        x + bar_width / 2,
        count2.values,
        width=bar_width,
        color="darkorange",
        edgecolor="black",
        label=station2
    )


    # --------------------------------------------------------
    # VALUE LABELS
    # --------------------------------------------------------
    for bars in [
        bar1,
        bar2
    ]:

        for bar in bars:

            value = bar.get_height()

            ax.annotate(
                f"{int(value)}",
                (
                    bar.get_x()
                    + bar.get_width() / 2,
                    value
                ),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9
            )


    # --------------------------------------------------------
    # GRAPH SETTINGS
    # --------------------------------------------------------

    ax.set_title(
        "Rainfall Data Distribution by Category",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Rainfall Data Category"
    )

    ax.set_ylabel(
        "Frequency"
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        rainfall_categories,
        rotation=15
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    # Legend outside graph
    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )
    download_plot(
        fig,
        f"rainfall_category_{station1}_{station2}_{target_year}.png",
        "download_rainfall_category_graph"
    )
    plt.close(fig)
    # ========================================================
    # CATEGORY TABLE
    # ========================================================
    st.subheader(
        "📋 Rainfall Data Category Frequency"
    )

    category_table = pd.DataFrame({

        "Rainfall Data Category":
            rainfall_categories,

        f"{station1} Frequency":
            count1.values,

        f"{station2} Frequency":
            count2.values

    })

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True
    )
    download_table(
        category_table,
        f"rainfall_category_{station1}_{station2}_{target_year}.csv",
        "download_rainfall_category_table"
    )
# ============================================================
# TAB 4 - YEARLY COMPARISON
# ============================================================
with tab4:
    st.subheader("📅 Yearly Rainfall Comparison")
    # --------------------------------------------------------
    # YEARLY TOTAL
    # --------------------------------------------------------
    yearly_total1 = (
        analysis1
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
    )
    yearly_total2 = (
        analysis2
        .set_index("YEAR")
        .reindex(common_years)["ANNUAL"]
    )
    # --------------------------------------------------------
    # YEARLY MEAN
    # --------------------------------------------------------
    yearly_mean1 = yearly_total1.mean(
        skipna=True
    )
    yearly_mean2 = yearly_total2.mean(
        skipna=True
    )
    # --------------------------------------------------------
    # DIFFERENCE
    # --------------------------------------------------------
    yearly_difference = (
        yearly_total1
        - yearly_total2
    )

    # --------------------------------------------------------
    # GRAPH
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(15, 8)
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
        label=f"{station1} Yearly Total"
    )

    bar2 = ax.bar(
        x + bar_width / 2,
        yearly_total2.values,
        width=bar_width,
        color="darkorange",
        edgecolor="black",
        label=f"{station2} Yearly Total"
    )

    # --------------------------------------------------------
    # MEAN LINES
    # --------------------------------------------------------

    ax.axhline(
        yearly_mean1,
        color="navy",
        linestyle="--",
        linewidth=2.5,
        label=f"{station1} Mean = {yearly_mean1:.1f} mm"
    )

    ax.axhline(
        yearly_mean2,
        color="crimson",
        linestyle="--",
        linewidth=2.5,
        label=f"{station2} Mean = {yearly_mean2:.1f} mm"
    )

    # --------------------------------------------------------
    # BAR VALUE LABELS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # GRAPH SETTINGS
    # --------------------------------------------------------

    ax.set_title(
        f"Yearly Rainfall Comparison\n"
        f"{station1} vs {station2}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Year"
    )

    ax.set_ylabel(
        "Rainfall (mm)"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        common_years,
        rotation=45
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    # Legend outside graph
    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )
    download_plot(
        fig,
        f"yearly_comparison_{station1}_{station2}.png",
        "download_yearly_comparison_graph"
    )
    plt.close(fig)
    # --------------------------------------------------------
    # MEAN SUMMARY
    # --------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            f"{station1} Yearly Mean",
            f"{yearly_mean1:.2f} mm"
        )

    with col2:

        st.metric(
            f"{station2} Yearly Mean",
            f"{yearly_mean2:.2f} mm"
        )

    # --------------------------------------------------------
    # YEARLY TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Yearly Rainfall Table"
    )

    yearly_comparison = pd.DataFrame({

        "Year":
            common_years,

        f"{station1} Total (mm)":
            yearly_total1.values,

        f"{station2} Total (mm)":
            yearly_total2.values,

        "Difference (mm)":
            yearly_difference.values

    })

    st.dataframe(
        yearly_comparison.round(2),
        use_container_width=True,
        hide_index=True
    )
    download_table(
        yearly_comparison.round(2),
        f"yearly_comparison_{station1}_{station2}.csv",
        "download_yearly_comparison_table"
    )
# ============================================================
# TAB 5- ERROR ANALYSIS
# ============================================================
with tab5:

    st.subheader(
        f"📏 Automatic vs Observation Error Analysis - {target_year}"
    )

    st.caption(
        f"Automatic Station: {station1} | "
        f"Observation: {station2}"
    )

    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Basic Difference",
            f"{basic_diff.mean(skipna=True):.2f} mm"
        )

    with col2:

        st.metric(
            "Percentage Difference",
            f"{percentage_diff.mean(skipna=True):.2f}%"
        )

    with col3:

        st.metric(
            "Mean Absolute Error (MAE)",
            f"{mae:.2f} mm"
        )


    # ========================================================
    # TABLE
    # ========================================================

    st.subheader(
        "📋 Monthly Error Analysis"
    )

    error_table = pd.DataFrame({

        "Month":
            MONTHS,

        f"Automatic ({station1}) (mm)":
            target1.values,

        f"Observation ({station2}) (mm)":
            target2.values,

        "Basic Difference (mm)":
            basic_diff.values,

        "Percentage Difference (%)":
            percentage_diff.values,

        "Absolute Error (mm)":
            absolute_error.values

    })

    st.dataframe(
        error_table.round(2),
        use_container_width=True,
        hide_index=True
    )
    download_table(
        error_table.round(2),
        f"error_analysis_{station1}_{station2}_{target_year}.csv",
        "download_error_analysis_table"
    )
    # ========================================================
    # X AXIS
    # ========================================================

    x = np.arange(
        len(MONTHS)
    )


    # ========================================================
    # BASIC DIFFERENCE GRAPH
    # ========================================================

    st.subheader(
        "📊 Basic Difference"
    )

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    bars = ax.bar(
        x,
        basic_diff.values,
        color="steelblue",
        edgecolor="black"
    )

    ax.axhline(
        0,
        color="black",
        linewidth=1
    )

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
                xytext=(
                    0,
                    5 if value >= 0 else -15
                ),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )

    ax.set_title(
        f"Basic Difference: "
        f"{station1} - {station2}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Month")

    ax.set_ylabel(
        "Difference (mm)"
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

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )
    download_plot(
        fig,
        f"basic_difference_{station1}_{station2}_{target_year}.png",
        "download_basic_difference_graph"
    )
    plt.close(fig)
    # ========================================================
    # PERCENTAGE DIFFERENCE GRAPH
    # ========================================================

    st.subheader(
        "📊 Percentage Difference"
    )

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    bars = ax.bar(
        x,
        percentage_diff.values,
        color="darkorange",
        edgecolor="black"
    )

    ax.axhline(
        0,
        color="black",
        linewidth=1
    )

    for bar in bars:

        value = bar.get_height()

        if pd.notna(value):

            ax.annotate(
                f"{value:.1f}%",
                (
                    bar.get_x()
                    + bar.get_width() / 2,
                    value
                ),
                xytext=(
                    0,
                    5 if value >= 0 else -15
                ),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )

    ax.set_title(
        f"Percentage Difference: "
        f"{station1} vs {station2}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Month")

    ax.set_ylabel(
        "Difference (%)"
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

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )
    download_plot(
        fig,
        f"percentage_difference_{station1}_{station2}_{target_year}.png",
        "download_percentage_difference_graph"
    )
    plt.close(fig)
    # ========================================================
    # MAE / ABSOLUTE ERROR GRAPH
    # ========================================================

    st.subheader(
        "📊 Monthly Absolute Error"
    )

    fig, ax = plt.subplots(
        figsize=(15, 7)
    )

    bars = ax.bar(
        x,
        absolute_error.values,
        color="seagreen",
        edgecolor="black"
    )

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
                fontsize=8
            )

    ax.set_title(
        f"Monthly Absolute Error "
        f"(Overall MAE = {mae:.2f} mm)",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Month")

    ax.set_ylabel(
        "Absolute Error (mm)"
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

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )
    download_plot(
        fig,
        f"mean_absolute_error_{station1}_{station2}_{target_year}.png",
        "download_mean_absolute_error_graph"
    )
    plt.close(fig)
# ============================================================
# TAB6 - MONTHLY BOXPLOT
# ============================================================

with tab6:

    st.subheader(
        "📦 Monthly Rainfall Boxplot"
    )

    st.caption(
        f"Distribution of monthly rainfall: "
        f"{station1} vs {station2}"
    )

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    box_data1 = []
    box_data2 = []

    for month in MONTHS:

        values1 = pd.to_numeric(
            analysis1[month],
            errors="coerce"
        ).dropna()

        values2 = pd.to_numeric(
            analysis2[month],
            errors="coerce"
        ).dropna()

        box_data1.append(
            values1.values
        )

        box_data2.append(
            values2.values
        )

    # --------------------------------------------------------
    # GRAPH
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(16, 8)
    )

    x = np.arange(
        len(MONTHS)
    )

    offset = 0.18

    # Station 1
    bp1 = ax.boxplot(
        box_data1,
        positions=x - offset,
        widths=0.30,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(
            marker="o",
            markersize=5,
            markerfacecolor="steelblue",
            markeredgecolor="black"
        )
    )

    # Station 2
    bp2 = ax.boxplot(
        box_data2,
        positions=x + offset,
        widths=0.30,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(
            marker="o",
            markersize=5,
            markerfacecolor="darkorange",
            markeredgecolor="black"
        )
    )

    # --------------------------------------------------------
    # BOX COLORS
    # --------------------------------------------------------

    for box in bp1["boxes"]:
        box.set_facecolor("steelblue")

    for box in bp2["boxes"]:
        box.set_facecolor("darkorange")

    # --------------------------------------------------------
    # MEDIAN
    # --------------------------------------------------------

    for median in bp1["medians"]:
        median.set_color("black")
        median.set_linewidth(2)

    for median in bp2["medians"]:
        median.set_color("black")
        median.set_linewidth(2)

    # --------------------------------------------------------
    # X AXIS
    # --------------------------------------------------------

    ax.set_xticks(x)

    ax.set_xticklabels(
        MONTHS
    )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    from matplotlib.patches import Patch

    legend_elements = [

        Patch(
            facecolor="steelblue",
            edgecolor="black",
            label=station1
        ),

        Patch(
            facecolor="darkorange",
            edgecolor="black",
            label=station2
        )

    ]

    ax.legend(
        handles=legend_elements,
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    # --------------------------------------------------------
    # GRAPH SETTINGS
    # --------------------------------------------------------

    ax.set_title(
        f"Monthly Rainfall Distribution\n"
        f"{station1} vs {station2}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Rainfall (mm)"
    )

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout(
        rect=[0, 0, 0.82, 1]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )
     # ========================================================
    # DOWNLOAD GRAPH
    # ========================================================

    download_plot(
        fig,
        f"monthly_boxplot_{station1}_{station2}.png",
        "download_boxplot_graph"
    )

    plt.close(fig)

    # ========================================================
    # BOXPLOT STATISTICS TABLE
    # ========================================================
    
    st.subheader(
        "📋 Monthly Boxplot Statistics"
    )
    
    boxplot_table = pd.DataFrame({
    
        "Month":
            MONTHS,
    
        f"File 1 - {station1} Min (mm)":
            [
                np.nanmin(x) if len(x) > 0 else np.nan
                for x in box_data1
            ],
    
        f"File 1 - {station1} Q1 (mm)":
            [
                np.percentile(x, 25)
                if len(x) > 0 else np.nan
                for x in box_data1
            ],
    
        f"File 1 - {station1} Median (mm)":
            [
                np.median(x)
                if len(x) > 0 else np.nan
                for x in box_data1
            ],
    
        f"File 1 - {station1} Q3 (mm)":
            [
                np.percentile(x, 75)
                if len(x) > 0 else np.nan
                for x in box_data1
            ],
    
        f"File 1 - {station1} Max (mm)":
            [
                np.nanmax(x) if len(x) > 0 else np.nan
                for x in box_data1
            ],
    
        f"File 2 - {station2} Min (mm)":
            [
                np.nanmin(x) if len(x) > 0 else np.nan
                for x in box_data2
            ],
    
        f"File 2 - {station2} Q1 (mm)":
            [
                np.percentile(x, 25)
                if len(x) > 0 else np.nan
                for x in box_data2
            ],
    
        f"File 2 - {station2} Median (mm)":
            [
                np.median(x)
                if len(x) > 0 else np.nan
                for x in box_data2
            ],
    
        f"File 2 - {station2} Q3 (mm)":
            [
                np.percentile(x, 75)
                if len(x) > 0 else np.nan
                for x in box_data2
            ],
    
        f"File 2 - {station2} Max (mm)":
            [
                np.nanmax(x) if len(x) > 0 else np.nan
                for x in box_data2
            ]
    })

st.dataframe(
    boxplot_table.round(2),
    use_container_width=True,
    hide_index=True
)

download_table(
    boxplot_table.round(2),
    f"monthly_boxplot_statistics_{station1}_{station2}.csv",
    "download_boxplot_table"
)
plt.close(fig)
# ============================================================
# TAB 7 - HEATMAP
# ============================================================
with tab7:

    st.subheader(
        "🔥 Monthly Rainfall Heatmap"
    )

    st.caption(
        f"Monthly rainfall distribution by year: "
        f"{station1} vs {station2}"
    )

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    heatmap1 = (
        analysis1
        .set_index("YEAR")
        .reindex(common_years)[MONTHS]
    )

    heatmap2 = (
        analysis2
        .set_index("YEAR")
        .reindex(common_years)[MONTHS]
    )

    # --------------------------------------------------------
    # CREATE FIGURE
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(16, 12)
    )

    # --------------------------------------------------------
    # STATION 1
    # --------------------------------------------------------

    im1 = axes[0].imshow(
        heatmap1.values,
        aspect="auto",
        cmap="YlGnBu"
    )

    axes[0].set_title(
        station1,
        fontsize=15,
        fontweight="bold"
    )

    axes[0].set_xticks(
        np.arange(len(MONTHS))
    )

    axes[0].set_xticklabels(
        MONTHS
    )

    axes[0].set_yticks(
        np.arange(len(common_years))
    )

    axes[0].set_yticklabels(
        common_years
    )

    axes[0].set_ylabel(
        "Year"
    )

    # --------------------------------------------------------
    # VALUE LABELS STATION 1
    # --------------------------------------------------------

    for i in range(len(common_years)):

        for j in range(len(MONTHS)):

            value = heatmap1.iloc[i, j]

            if pd.notna(value):

                axes[0].text(
                    j,
                    i,
                    f"{value:.0f}",
                    ha="center",
                    va="center",
                    fontsize=7
                )

    fig.colorbar(
        im1,
        ax=axes[0],
        label="Rainfall (mm)"
    )

    # --------------------------------------------------------
    # STATION 2
    # --------------------------------------------------------

    im2 = axes[1].imshow(
        heatmap2.values,
        aspect="auto",
        cmap="YlOrRd"
    )

    axes[1].set_title(
        station2,
        fontsize=15,
        fontweight="bold"
    )

    axes[1].set_xticks(
        np.arange(len(MONTHS))
    )

    axes[1].set_xticklabels(
        MONTHS
    )

    axes[1].set_yticks(
        np.arange(len(common_years))
    )

    axes[1].set_yticklabels(
        common_years
    )

    axes[1].set_xlabel(
        "Month"
    )

    axes[1].set_ylabel(
        "Year"
    )

    # --------------------------------------------------------
    # VALUE LABELS STATION 2
    # --------------------------------------------------------

    for i in range(len(common_years)):

        for j in range(len(MONTHS)):

            value = heatmap2.iloc[i, j]

            if pd.notna(value):

                axes[1].text(
                    j,
                    i,
                    f"{value:.0f}",
                    ha="center",
                    va="center",
                    fontsize=7
                )

    fig.colorbar(
        im2,
        ax=axes[1],
        label="Rainfall (mm)"
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    fig.suptitle(
        "Monthly Rainfall Heatmap",
        fontsize=18,
        fontweight="bold"
    )

    plt.tight_layout(
        rect=[0, 0, 1, 0.96]
    )

    st.pyplot(
        fig,
        use_container_width=True
    )
        # ========================================================
    # DOWNLOAD HEATMAP GRAPH
    # ========================================================

    download_plot(
        fig,
        f"monthly_heatmap_{station1}_{station2}.png",
        "download_heatmap_graph"
    )

    plt.close(fig)

    # ========================================================
    # HEATMAP TABLE - STATION 1
    # ========================================================

    st.subheader(
        f"📋 Monthly Rainfall Table - {station1}"
    )

    heatmap_table1 = heatmap1.reset_index()

    st.dataframe(
        heatmap_table1.round(2),
        use_container_width=True,
        hide_index=True
    )

    download_table(
        heatmap_table1.round(2),
        f"monthly_heatmap_{station1}.csv",
        "download_heatmap_table1"
    )

    # ========================================================
    # HEATMAP TABLE - STATION 2
    # ========================================================

    st.subheader(
        f"📋 Monthly Rainfall Table - {station2}"
    )

    heatmap_table2 = heatmap2.reset_index()

    st.dataframe(
        heatmap_table2.round(2),
        use_container_width=True,
        hide_index=True
    )

    download_table(
        heatmap_table2.round(2),
        f"monthly_heatmap_{station2}.csv",
        "download_heatmap_table2"
    )
    plt.close(fig)
