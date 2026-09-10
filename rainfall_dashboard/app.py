import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import calendar
import io
import streamlit as st
import xlrd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Rainfall Analysis",
    page_icon="🌧️",
    layout="wide"
)

st.title("🌧️ Rainfall Data Analysis")
st.caption("Pemprosesan, Quality Control dan Analisis Data Hujan")
# ============================================================
# MONTHS
# ============================================================
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# ============================================================
# GRAPH SETTINGS
# ============================================================
RAINFALL_MIN = 0
RAINFALL_MAX = 500
# ============================================================
# FIGURE SIZE
# ============================================================
FIG_WIDTH = 14
FIG_HEIGHT = 9
# ============================================================
# FILE UPLOAD
# ============================================================
uploaded_files = st.file_uploader("📁 Upload Excel file data hujan",
    type=["xlsx", "xls"],
    accept_multiple_files=True)

if not uploaded_files:
    st.info("Sila upload sekurang-kurangnya satu fail Excel.")
    st.stop()
# ============================================================
# DETECT AVAILABLE YEARS
# ============================================================
def get_available_years(uploaded_file):

    try:
        file_bytes = uploaded_file.getvalue()
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()

        if file_ext == ".xls":
            engine = "xlrd"
        else:
            engine = "openpyxl"

        excel_file = pd.ExcelFile(io.BytesIO(file_bytes),engine=engine)
        available_years = []

        for sheet in excel_file.sheet_names:
            try:
                year = int(str(sheet).strip())
                if 1900 <= year <= 2100:
                    available_years.append(year)

            except:
                continue

        return sorted(set(available_years))

    except Exception:

        return []
# ============================================================
# DETECT YEARS FROM ALL UPLOADED FILES
# ============================================================
all_available_years = set()

file_years = {}

for uploaded_file in uploaded_files:
    detected_years = get_available_years(uploaded_file)

    file_years[uploaded_file.name] = detected_years
    all_available_years.update(detected_years)

all_available_years = sorted(all_available_years)
# ============================================================
# TAHUN CLIMATOLOGY
# ============================================================
st.sidebar.subheader("📅 Climatology Period")

START_YEAR = st.sidebar.selectbox(
    "Start Year",
    all_available_years,
    index=0
)

END_YEAR = st.sidebar.selectbox(
    "End Year",
    all_available_years,
    index=len(all_available_years) - 1
)

if START_YEAR > END_YEAR:
    st.sidebar.error("Start Year mesti lebih kecil atau sama dengan End Year.")
    st.stop()

years = range(int(START_YEAR),int(END_YEAR) + 1)

YEAR_RANGE_TEXT = (f"{int(START_YEAR)}–{int(END_YEAR)}")
# ============================================================
# SIDEBAR SETTINGS
# ============================================================
st.sidebar.header("⚙️ Analysis Settings")
# ============================================================
# WMO MISSING DATA RULE
# ============================================================
st.sidebar.subheader("WMO Missing Data Rule")

MAX_MISSING_DAYS = st.sidebar.number_input(
    "Maximum missing days",
    min_value=0,
    max_value=31,
    value=10,
    step=1,
    help=("Bulan ditolak jika bilangan missing days melebihi nilai ini. Default 10 bermaksud >=11 missing days ditolak.")
)

MAX_CONSECUTIVE_MISSING = st.sidebar.number_input(
    "Maximum consecutive missing days",
    min_value=1,
    max_value=31,
    value=4,
    step=1,
    help=("Bulan ditolak jika terdapat missing days berturut-turut melebihi nilai ini. Default 4 bermaksud >=5 berturut-turut ditolak.")
)
# ============================================================
# RAINFALL THRESHOLDS
# ============================================================
st.sidebar.subheader("🌧️ Rainfall Threshold")

VALID_MIN = 0.0

WET_DAY_MIN = st.sidebar.number_input(
    "Wet day threshold (mm)",
    min_value=0.0,
    value=0.1,
    step=0.01
)

SUSPECT_RAINFALL = st.sidebar.number_input(
    "Suspect threshold (mm)",
    min_value=0.0,
    value=150.0,
    step=10.0
)

EXTREME_RAINFALL = st.sidebar.number_input(
    "Extreme threshold (mm)",
    min_value=0.0,
    value=250.0,
    step=10.0
)
# ============================================================
# PLOT SETTINGS - USER BOLEH UBAH
# ============================================================
st.sidebar.header("🎨 Plot Settings")

# ============================================================
# BACKGROUND
# ============================================================
BG_COLOR = st.sidebar.color_picker(
    "Background Graf",
    "#FFFFFF"
)
# ============================================================
# DEFAULT BAR COLORS - MONTHLY RAINFALL
# ============================================================
default_colors = [
    "#4682B4",  # Jan
    "#87CEEB",  # Feb
    "#3CB371",  # Mar
    "#32CD32",  # Apr
    "#FFD700",  # May
    "#FFA500",  # Jun
    "#FF7F50",  # Jul
    "#FF6347",  # Aug
    "#9370DB",  # Sep
    "#DA70D6",  # Oct
    "#6A5ACD",  # Nov
    "#008080"   # Dec
]
# ============================================================
# SESSION STATE
# ============================================================
if "bar_colors" not in st.session_state:
    st.session_state.bar_colors = default_colors.copy()

if "max_daily_color" not in st.session_state:
    st.session_state.max_daily_color = "#FF6347"

if "wet_days_color" not in st.session_state:
    st.session_state.wet_days_color = "#3CB371"

if "std_color" not in st.session_state:
    st.session_state.std_color = "#9370DB"

if "hist_color" not in st.session_state:
    st.session_state.hist_color = "#4682B4"
# ============================================================
# SELECT BAR CHART
# ============================================================
chart_options = ["Bar + Line",]

selected_chart = st.sidebar.selectbox("Select Bar Chart",chart_options)
# ============================================================
# MONTHLY RAINFALL
# ============================================================
if selected_chart == "Monthly Rainfall":
    selected_month = st.sidebar.selectbox("Select Month",months)
    selected_index = months.index(selected_month)

    st.session_state.bar_colors[
        selected_index
    ] = st.sidebar.color_picker(
        f"{selected_month} Bar Colour",
        st.session_state.bar_colors[selected_index]
    )
# ============================================================
# MEAN LINE
# ============================================================
LINE_COLOR = st.sidebar.color_picker(
    "Mean Line",
    "#000000"
)
# ============================================================
# MINIMUM
# ============================================================
MIN_COLOR = st.sidebar.color_picker(
    "Minimum",
    "#008000"
)
# ============================================================
# MAXIMUM
# ============================================================
MAX_COLOR = st.sidebar.color_picker(
    "Maximum",
    "#FF0000"
)
# ============================================================
# CHECK AVAILABLE YEARS
# ============================================================
if not all_available_years:
    st.error("❌ Tiada sheet tahun yang sah dijumpai dalam fail Excel.")
    st.stop()

# ============================================================
# FUNCTION
# MAXIMUM CONSECUTIVE MISSING
# ============================================================
def max_consecutive_missing(values):
    is_missing = values.isna()
    max_missing = 0
    current_missing = 0

    for missing in is_missing:
        
        if missing:
            current_missing += 1

            if current_missing > max_missing:
                max_missing = current_missing

        else:
            current_missing = 0

    return max_missing
# ============================================================
# FUNCTION
# READ YEAR SHEET
# ============================================================
def read_year_sheet(uploaded_file, year):

    try:
        file_bytes = uploaded_file.getvalue()

        file_ext = os.path.splitext(
            uploaded_file.name
        )[1].lower()
        
        if file_ext == ".xls":
            engine = "xlrd"
        elif file_ext == ".xlsx":
            engine = "openpyxl"
        else:
            return None, "Format fail tidak disokong."

        df = pd.read_excel(
            io.BytesIO(file_bytes),
            sheet_name=str(year),
            header=6,
            engine=engine
        )

    except Exception as e:
        return None, str(e)

    if df is None or df.empty:
        return None, "Sheet kosong."
    # --------------------------------------------------------
    # Ambil 13 column pertama
    # --------------------------------------------------------
    if df.shape[1] < 13:

        return None, (
            f"Bilangan column tidak mencukupi "
            f"({df.shape[1]} column dikesan). "
            f"Minimum 13 column diperlukan."
        )

    df = df.iloc[:, :13].copy()

    df.columns = [
        "hari",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    # --------------------------------------------------------
    # Convert day
    # --------------------------------------------------------
    df["hari"] = pd.to_numeric(
        df["hari"],
        errors="coerce"
    )

    df = df[
        df["hari"].between(1, 31)
    ].copy()
    # --------------------------------------------------------
    # Convert rainfall
    # --------------------------------------------------------
    for month in months:

        df[month] = pd.to_numeric(
            df[month],
            errors="coerce"
        )

        # Negative = invalid
        df.loc[
            df[month] < VALID_MIN,
            month
        ] = np.nan

    df["Year"] = int(year)

    return df, None
# ============================================================
# FUNCTION
# ANALYZE ONE FILE
# ============================================================
def analyze_file(uploaded_file):

    file_name = os.path.splitext(
        uploaded_file.name
    )[0]

    original_file_name = uploaded_file.name

    daily_results = []
    read_errors = []    
    # ========================================================
    # READ ALL YEARS
    # ========================================================
    for year in years:

        df, error = read_year_sheet(
            uploaded_file,
            year
        )

        if df is not None:
            daily_results.append(df)

        else:
            read_errors.append({
                "Year": int(year),
                "Error": error
            })
    # ========================================================
    # CHECK DATA
    # ========================================================
    if len(daily_results) == 0:

        return {
            "success": False,
            "file_name": file_name,
            "original_file_name": original_file_name,
            "error": "Tiada sheet tahun berjaya dibaca."
        }
    # ========================================================
    # COMBINE DATA
    # ========================================================
    all_daily = pd.concat(
        daily_results,
        ignore_index=True
    )
    # ========================================================
    # QUALITY CONTROL
    # ========================================================
    for month in months:

        all_daily.loc[
            all_daily[month] < VALID_MIN,
            month
        ] = np.nan
    # ========================================================
    # SUSPECT & EXTREME
    # ========================================================
    suspect_records = []
    extreme_records = []

    for _, row in all_daily.iterrows():
        year = int(row["Year"])
        day = int(row["hari"])

        for month in months:
            value = row[month]

            if pd.isna(value):
                continue

            if value > EXTREME_RAINFALL:
                extreme_records.append({
                    "Year": year,
                    "Day": day,
                    "Month": month,
                    "Rainfall (mm)": value,
                    "Status": "EXTREME - DOUBLE CHECK"
                })

            elif value > SUSPECT_RAINFALL:
                suspect_records.append({
                    "Year": year,
                    "Day": day,
                    "Month": month,
                    "Rainfall (mm)": value,
                    "Status": "SUSPECT - SEMAK"
                })

    suspect_df = pd.DataFrame(
        suspect_records,
        columns=[
            "Year",
            "Day",
            "Month",
            "Rainfall (mm)",
            "Status"
        ]
    )

    extreme_df = pd.DataFrame(
        extreme_records,
        columns=[
            "Year",
            "Day",
            "Month",
            "Rainfall (mm)",
            "Status"
        ]
    )
    # ========================================================
    # YEARLY MONTHLY TOTAL
    # ========================================================
    available_years = sorted(
        all_daily["Year"].unique()
    )

    yearly_monthly_total = pd.DataFrame(
        index=available_years,
        columns=months,
        dtype=float
    )

    monthly_missing_count = pd.DataFrame(
        index=available_years,
        columns=months,
        dtype=float
    )

    monthly_valid_count = pd.DataFrame(
        index=available_years,
        columns=months,
        dtype=float
    )

    monthly_max_consecutive_missing = pd.DataFrame(
        index=available_years,
        columns=months,
        dtype=float
    )

    monthly_qc_status = pd.DataFrame(
        index=available_years,
        columns=months,
        dtype=object
    )
    # ========================================================
    # LOOP YEAR & MONTH
    # ========================================================
    for year in available_years:
        year_data = all_daily[all_daily["Year"] == year]

        for month in months:
            month_index = (months.index(month) + 1)

            days_expected = calendar.monthrange(
                int(year),
                month_index
            )[1]

            values = (
                year_data[month]
                .iloc[:days_expected]
                .copy()
            )

            valid_values = values[
                values.notna() &
                (values >= VALID_MIN)
            ]

            valid_count = len(valid_values)
            missing_count = (days_expected - valid_count)
            max_consecutive = (max_consecutive_missing(values))

            monthly_valid_count.loc[year,month] = valid_count
            monthly_missing_count.loc[year,month] = missing_count
            monthly_max_consecutive_missing.loc[year,month] = max_consecutive
            # ------------------------------------------------
            # ACCEPT / REJECT
            # Default:
            # >10 missing = reject
            # >=5 consecutive = reject
            # ------------------------------------------------
            if (
                missing_count <= MAX_MISSING_DAYS
                and
                max_consecutive <= MAX_CONSECUTIVE_MISSING
            ):

                yearly_monthly_total.loc[year,month] = valid_values.sum()
                monthly_qc_status.loc[year,month] = "ACCEPT"

            else:
                yearly_monthly_total.loc[year,month] = np.nan

                if missing_count > MAX_MISSING_DAYS:
                    monthly_qc_status.loc[year,month] = (f"REJECT: >{MAX_MISSING_DAYS} MISSING")

                elif (max_consecutive >MAX_CONSECUTIVE_MISSING):
                    monthly_qc_status.loc[year,month
                    ] = (f"REJECT: {MAX_CONSECUTIVE_MISSING} CONSECUTIVE MISSING")

                else:
                    monthly_qc_status.loc[year,month] = "REJECT"
    # ========================================================
    # CLIMATOLOGICAL MONTHLY MEAN
    # ========================================================
    mean_monthly_total = (
        yearly_monthly_total
        .mean(
            axis=0,
            skipna=True
        )
        .reindex(months)
    )
    # ========================================================
    # YEARLY TOTAL
    # ========================================================
    yearly_total = (
        yearly_monthly_total
        .sum(
            axis=1,
            min_count=1
        )
    )
    # ========================================================
    # RETURN RESULTS
    # ========================================================
    return {
        "success": True,
        "file_name":file_name,
        "original_file_name":original_file_name,
        "all_daily":all_daily,
        "yearly_monthly_total":yearly_monthly_total,
        "monthly_missing_count":monthly_missing_count,
        "monthly_valid_count":monthly_valid_count,
        "monthly_max_consecutive_missing":monthly_max_consecutive_missing,
        "monthly_qc_status":monthly_qc_status,
        "mean_monthly_total":mean_monthly_total,
        "yearly_total":yearly_total,
        "suspect_df":suspect_df,
        "extreme_df":extreme_df,
        "read_errors":read_errors
    }
# ============================================================
# PROCESS ALL UPLOADED FILES
# ============================================================
with st.spinner(
    "⏳ Sedang memproses semua fail Excel..."
):

    results = []
    progress_bar = st.progress(0)

    for i, uploaded_file in enumerate(
        uploaded_files
    ):

        result = analyze_file(
            uploaded_file
        )

        results.append(result)

        progress_bar.progress(
            int(
                ((i + 1) /
                 len(uploaded_files)) * 100
            )
        )

    progress_bar.empty()

# ============================================================
# CHECK RESULTS
# ============================================================
successful_results = [
    result
    for result in results
    if result.get("success", False)
]

failed_results = [
    result
    for result in results
    if not result.get("success", False)
]
# ============================================================
# TARGET YEAR
# ============================================================
available_years = sorted(
    set(
        year
        for result in successful_results
        for year in result["all_daily"]["Year"].dropna().unique()
    )
)

target_year = st.sidebar.selectbox(
    "📅 Target Year",
    available_years,
    index=len(available_years) - 1,
    key="target_year"
)

target_year = int(target_year)
# ============================================================
# TARGET YEAR ANALYSIS
# ============================================================
for result in successful_results:
    all_daily = result["all_daily"]
    yearly_monthly_total = (result["yearly_monthly_total"])
    mean_monthly_total = (result["mean_monthly_total"])
    # --------------------------------------------------------
    # TARGET YEAR MONTHLY TOTAL
    # --------------------------------------------------------
    if target_year in yearly_monthly_total.index:
        rainfall_target = (yearly_monthly_total.loc[target_year].reindex(months))

    else:
        rainfall_target = pd.Series(np.nan,index=months)
    # --------------------------------------------------------
    # ANOMALY
    # --------------------------------------------------------
    anomaly_percent = ((rainfall_target - mean_monthly_total)/ mean_monthly_total) * 100
    anomaly_percent[mean_monthly_total == 0] = np.nan
    # --------------------------------------------------------
    # MIN / MAX TARGET YEAR
    # --------------------------------------------------------
    valid_target = rainfall_target.dropna()

    if len(valid_target) > 0:
        min_target_month = valid_target.idxmin()
        min_target_value = valid_target.min()

        max_target_month = valid_target.idxmax()
        max_target_value = valid_target.max()

    else:
        min_target_month = None
        min_target_value = None
        max_target_month = None
        max_target_value = None
    # --------------------------------------------------------
    # MIN / MAX MEAN
    # --------------------------------------------------------
    valid_mean = mean_monthly_total.dropna()

    if len(valid_mean) > 0:
        min_mean_month = valid_mean.idxmin()
        min_mean_value = valid_mean.min()

        max_mean_month = valid_mean.idxmax()
        max_mean_value = valid_mean.max()

    else:
        min_mean_month = None
        min_mean_value = None
        max_mean_month = None
        max_mean_value = None
    # ========================================================
    # SAVE INTO RESULT
    # ========================================================
    result["rainfall_target"] = rainfall_target
    result["anomaly_percent"] = anomaly_percent

    result["min_target_month"] = min_target_month
    result["min_target_value"] = min_target_value
    result["max_target_month"] = max_target_month
    result["max_target_value"] = max_target_value

    result["min_mean_month"] = min_mean_month
    result["min_mean_value"] = min_mean_value
    result["max_mean_month"] = max_mean_month
    result["max_mean_value"] = max_mean_value
# ============================================================
# DAILY STATISTICS FOR TARGET YEAR
# ============================================================
for result in successful_results:

    all_daily = result["all_daily"]

    target_data = all_daily[
        all_daily["Year"] == target_year
    ].copy()

    median_daily = []
    std_daily = []
    max_daily = []
    min_daily = []
    wet_days = []
    valid_data_percent = []
    suspect_count = []
    extreme_count = []

    # ========================================================
    # RAINFALL CATEGORY
    # ========================================================
    category_labels = [
        "Slight Rain (1.0–10.0 mm)",
        "Moderate Rain (>10.0–30.0 mm)",
        "Heavy Rain (>30.0–60.0 mm)",
        "Very Heavy Rain (>60 mm)"
    ]

    # ========================================================
    # MONTHLY DAILY STATISTICS
    # ========================================================
    for month in months:

        month_index = months.index(month) + 1

        days_expected = calendar.monthrange(
            target_year,
            month_index
        )[1]

        raw_values = (
            target_data[month]
            .iloc[:days_expected]
            .copy()
        )

        # ----------------------------------------------------
        # QC
        # ----------------------------------------------------
        qc_values = raw_values[
            raw_values.notna() &
            (raw_values >= VALID_MIN)
        ]

        # ----------------------------------------------------
        # WET DAYS
        # ----------------------------------------------------
        values = qc_values[
            qc_values >= WET_DAY_MIN
        ]

        # ----------------------------------------------------
        # VALID DATA %
        # ----------------------------------------------------
        valid_count = len(qc_values)

        percent = (
            valid_count /
            days_expected
        ) * 100

        valid_data_percent.append(percent)

        # ----------------------------------------------------
        # MEDIAN
        # ----------------------------------------------------
        if len(values) > 0:
            median_daily.append(
                values.median()
            )
        else:
            median_daily.append(np.nan)

        # ----------------------------------------------------
        # STANDARD DEVIATION
        # ----------------------------------------------------
        if len(values) > 1:
            std_daily.append(
                values.std()
            )
        else:
            std_daily.append(np.nan)

        # ----------------------------------------------------
        # MAXIMUM
        # ----------------------------------------------------
        if len(values) > 0:
            max_daily.append(
                values.max()
            )
        else:
            max_daily.append(np.nan)

        # ----------------------------------------------------
        # MINIMUM
        # ----------------------------------------------------
        if len(values) > 0:
            min_daily.append(
                values.min()
            )
        else:
            min_daily.append(np.nan)

        # ----------------------------------------------------
        # WET DAYS
        # ----------------------------------------------------
        wet_days.append(
            (qc_values >= WET_DAY_MIN).sum()
        )

        # ----------------------------------------------------
        # SUSPECT
        # ----------------------------------------------------
        suspect_count.append(
            (values > SUSPECT_RAINFALL).sum()
        )

        # ----------------------------------------------------
        # EXTREME
        # ----------------------------------------------------
        extreme_count.append(
            (values > EXTREME_RAINFALL).sum()
        )

    # ========================================================
    # ANALYSIS TABLE
    # ========================================================
    analysis_table = pd.DataFrame({
        "Month": months,
        "Median": median_daily,
        "Std Dev": std_daily,
        "Maximum": max_daily,
        "Minimum": min_daily,
        "Wet Days": wet_days,
        "Valid Data (%)": valid_data_percent,
        "Suspect": suspect_count,
        "Extreme": extreme_count
    })

    # ========================================================
    # HISTOGRAM VALUES
    # ========================================================
    hist_values = target_data[
        months
    ].stack()

    hist_values = hist_values[
        hist_values.notna() &
        (hist_values >= VALID_MIN)
    ]

    # ========================================================
    # RAINFALL CATEGORY
    # ========================================================
    all_values = target_data[
        months
    ].stack()

    all_values = all_values[
        all_values.notna() &
        (all_values >= VALID_MIN)
    ]

    category_values = [
        (
            (all_values >= 1) &
            (all_values <= 10)
        ).sum(),

        (
            (all_values > 10) &
            (all_values <= 30)
        ).sum(),

        (
            (all_values > 30) &
            (all_values <= 60)
        ).sum(),

        (all_values > 60).sum()
    ]

    # ========================================================
    # SAVE INTO RESULT
    # ========================================================
    result["median_daily"] = median_daily
    result["std_daily"] = std_daily
    result["max_daily"] = max_daily
    result["min_daily"] = min_daily
    result["wet_days"] = wet_days
    result["valid_data_percent"] = valid_data_percent
    result["suspect_count"] = suspect_count
    result["extreme_count"] = extreme_count

    result["analysis_table"] = analysis_table
    result["hist_values"] = hist_values
    result["category_values"] = category_values
    result["category_labels"] = category_labels
# ============================================================
# FILE SUMMARY
# ============================================================
st.success(
    f"✅ {len(successful_results)} daripada "
    f"{len(uploaded_files)} fail berjaya dianalisis."
)

if failed_results:
    st.warning(
        f"⚠️ {len(failed_results)} fail tidak berjaya dianalisis."
    )

    for result in failed_results:
        st.error(
            f"{result.get('original_file_name', 'Unknown')}: "
            f"{result.get('error', 'Unknown error')}"
        )

if not successful_results:
    st.stop()
# ============================================================
# STATION SELECTION
# ============================================================
station_options = [
    result["file_name"]
    for result in successful_results
]

selected_station = st.sidebar.selectbox(
    "📍 Select Station",
    station_options,
    key="main_station"
)

# ============================================================
# FILTER DISPLAY RESULT
# ============================================================
display_results = [
    result
    for result in successful_results
    if result["file_name"] in selected_station
]

if not selected_station:
    st.warning("Sila pilih sekurang-kurangnya satu stesen.")
    st.stop()
# ============================================================
# GLOBAL AUTO Y-AXIS
# ============================================================
global_max_total = 0
global_max_mean = 0

max_total_file = None
max_total_month = None

max_mean_file = None
max_mean_month = None

for result in successful_results:
    rainfall_target = result["rainfall_target"]
    
    mean_monthly_total = result["mean_monthly_total"]

    if rainfall_target.notna().any():
        local_max = rainfall_target.max()

        if local_max > global_max_total:
            global_max_total = local_max

            max_total_file = result["original_file_name"]

            max_total_month = (rainfall_target.idxmax())

    if mean_monthly_total.notna().any():
        local_max = mean_monthly_total.max()

        if local_max > global_max_mean:
            global_max_mean = local_max

            max_mean_file = result["original_file_name"]
            max_mean_month = (mean_monthly_total.idxmax())

selected_max = max(
    global_max_total,
    global_max_mean
)

if selected_max > 0:
    RAINFALL_MAX = (int(selected_max / 100) + 1) * 100

else:
    RAINFALL_MAX = 100

# ============================================================
# GLOBAL SUMMARY
# ============================================================
st.subheader("📌 Overall Analysis Summary")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric(
        "Files Analysed",
        len(successful_results)
    )

with summary_col2:
    st.metric(
        "Target Year",
        target_year
    )

with summary_col3:
    st.metric(
        "Auto Y-Axis Maximum",
        f"{RAINFALL_MAX:.0f} mm"
    )

# ============================================================
# GLOBAL AUTO Y-AXIS INFORMATION
# ============================================================
with st.expander(
    "🔎 Auto Y-Axis Information"
):

    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Maximum Target-Year Monthly Total**")
        st.write(f"Value: {global_max_total:.2f} mm")
        st.write(f"File: {max_total_file}")
        st.write(f"Month: {max_total_month}")

    with col2:
        st.write("**Maximum Climatological Monthly Mean**")
        st.write(f"Value: {global_max_mean:.2f} mm")
        st.write(f"File: {max_mean_file}")
        st.write(f"Month: {max_mean_month}")
# ============================================================
# MAIN TABS
# ============================================================
main_tabs = st.tabs([
    "📅 Target Year (Selected Station)",
    "📊 All Years (Selected Station)",
    "🔄 Station Comparison (All years data)",
    "🌧️ Highest Daily Rainfall (30 Years)"
])

with main_tabs[0]:
    # ============================================================
    # DISPLAY EACH FILE
    # ============================================================
    for result in display_results:
        file_name = result["file_name"]
        original_file_name = result["original_file_name"]
        all_daily = result["all_daily"]

        target_data = all_daily[
            all_daily["Year"] == target_year
        ].copy()
    
        yearly_monthly_total = result["yearly_monthly_total"]
        monthly_missing_count = result["monthly_missing_count"]
        monthly_valid_count = result["monthly_valid_count"]
        monthly_max_consecutive_missing = result["monthly_max_consecutive_missing"]
        monthly_qc_status = result["monthly_qc_status"]
        rainfall_target = result["rainfall_target"]
        mean_monthly_total = result["mean_monthly_total"]
        anomaly_percent = result["anomaly_percent"]
        min_target_month = result["min_target_month"]
        min_target_value = result["min_target_value"]
        max_target_month = result["max_target_month"]
        max_target_value = result["max_target_value"]
        min_mean_month = result["min_mean_month"]
        min_mean_value = result["min_mean_value"]
        max_mean_month = result["max_mean_month"]
        max_mean_value = result["max_mean_value"]
        median_daily = result["median_daily"]
        std_daily = result["std_daily"]
        max_daily = result["max_daily"]
        min_daily = result["min_daily"]
        wet_days = result["wet_days"]
        valid_data_percent = result["valid_data_percent"]
        analysis_table = result["analysis_table"]
        suspect_df = result["suspect_df"]
        extreme_df = result["extreme_df"]
        hist_values = result["hist_values"]
        category_values = result["category_values"]
        category_labels = result["category_labels"]
        read_errors = result["read_errors"]
        
        # ========================================================
        # FILE HEADER
        # ========================================================
        st.divider()
    
        st.header(f"📁 {original_file_name}")
        # ========================================================
        # READ ERROR
        # ========================================================
        if read_errors:
    
            with st.expander("⚠️ Sheet yang tidak berjaya dibaca"):
                error_df = pd.DataFrame(read_errors)
    
                st.dataframe(error_df,use_container_width=True,hide_index=True)
        # ========================================================
        # BASIC METRICS
        # ========================================================
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            if (
                min_target_month is not None
                and min_target_value is not None
            ):
    
                st.metric(
                    f"Minimum {target_year}",
                    f"{min_target_value:.2f} mm",
                    min_target_month
                )
    
            else:
                st.metric(
                    f"Minimum {target_year}",
                    "N.A."
                )
    
        with col2:
            if (
                max_target_month is not None
                and max_target_value is not None
            ):
    
                st.metric(
                    f"Maximum {target_year}",
                    f"{max_target_value:.2f} mm",
                    max_target_month
                )
    
            else:
                st.metric(
                    f"Maximum {target_year}",
                    "N.A."
                )
    
        with col3:
            if (
                min_mean_month is not None
                and min_mean_value is not None
            ):

                st.metric(
                    "Minimum Mean",
                    f"{min_mean_value:.2f} mm",
                    min_mean_month
                )
    
            else:
                st.metric(
                    "Minimum Mean",
                    "N.A."
                )
    
        with col4:
            if (
                max_mean_month is not None
                and max_mean_value is not None
            ):
    
                st.metric(
                    "Maximum Mean",
                    f"{max_mean_value:.2f} mm",
                    max_mean_month
                )
    
            else:
                st.metric(
                    "Maximum Mean",
                    "N.A."
                )

        # ========================================================
        # YEARS AVAILABLE
        # ========================================================
        years_available = (
            all_daily["Year"]
            .dropna()
            .nunique()
        )
        # ========================================================
        # QC SUMMARY
        # ========================================================
        qc_col1, qc_col2, qc_col3 = st.columns(3)
    
        with qc_col1:
            st.metric("Suspect Records",len(suspect_df))
    
        with qc_col2:
            st.metric("Extreme Records",len(extreme_df))
    
        with qc_col3:
            st.metric("Valid Daily Records",int((all_daily[months].notna().sum().sum())))

# ============================================================
# MAIN TAB 4 — HIGHEST DAILY RAINFALL
# ============================================================

with main_tabs[3]:

    st.header(
        f"🌧️ Highest Daily Rainfall {YEAR_RANGE_TEXT}"
    )

    # ========================================================
    # TEMPOH ANALISIS
    # ========================================================

    period_years = (
        int(END_YEAR)
        - int(START_YEAR)
        + 1
    )

    if period_years != 30:

        st.warning(
            f"⚠️ Tempoh yang dipilih ialah "
            f"{period_years} tahun "
            f"({int(START_YEAR)}–{int(END_YEAR)}). "
            "Untuk analisis tepat 30 tahun, sila tetapkan "
            "Start Year dan End Year supaya merangkumi 30 tahun."
        )

    st.info(
        "Analisis ini mencari rekod hujan harian tertinggi "
        "daripada semua stesen bagi semua tahun dalam tempoh "
        f"{YEAR_RANGE_TEXT}. Nilai kosong dan nilai di bawah "
        "0.1 mm tidak diambil kira."
    )

    # ========================================================
    # KUMPUL DATA SEMUA STESEN
    # ========================================================

    highest_records = []

    for result in successful_results:

        all_daily_station = (
            result["all_daily"].copy()
        )

        station_name = result["file_name"]

        period_data = all_daily_station[
            all_daily_station["Year"].between(
                int(START_YEAR),
                int(END_YEAR)
            )
        ].copy()

        if period_data.empty:
            continue

        daily_long = period_data.melt(
            id_vars=["Year", "hari"],
            value_vars=months,
            var_name="Month",
            value_name="Rainfall (mm)"
        )

        daily_long["Rainfall (mm)"] = pd.to_numeric(
            daily_long["Rainfall (mm)"],
            errors="coerce"
        )

        daily_long = daily_long[
            daily_long["Rainfall (mm)"].notna()
            &
            (
                daily_long["Rainfall (mm)"]
                >= VALID_MIN
            )
        ].copy()

        if daily_long.empty:
            continue

        month_number = {
            month: i + 1
            for i, month in enumerate(months)
        }

        daily_long["Month Number"] = (
            daily_long["Month"].map(month_number)
        )

        daily_long["Date"] = pd.to_datetime(
            dict(
                year=daily_long["Year"].astype(int),
                month=daily_long["Month Number"].astype(int),
                day=daily_long["hari"].astype(int)
            ),
            errors="coerce"
        )

        daily_long = daily_long[
            daily_long["Date"].notna()
        ].copy()

        daily_long["Station"] = station_name

        highest_records.append(
            daily_long[
                [
                    "Date",
                    "Year",
                    "Month",
                    "hari",
                    "Station",
                    "Rainfall (mm)"
                ]
            ]
        )

    # ========================================================
    # CHECK DATA
    # ========================================================

    if not highest_records:

        st.warning(
            "⚠️ Tiada data hujan yang sah untuk dianalisis."
        )

        st.stop()

    highest_daily_df = pd.concat(
        highest_records,
        ignore_index=True
    )

    highest_daily_df = (
        highest_daily_df
        .sort_values(
            "Rainfall (mm)",
            ascending=False
        )
        .reset_index(drop=True)
    )

    highest_daily_df["Rank"] = (
        highest_daily_df.index + 1
    )

# ========================================================
    # PILIH STESEN
    # ========================================================
    
    station_options = sorted(
        highest_daily_df["Station"].dropna().unique()
    )
    
    selected_station_rainfall = st.selectbox(
        "🏢 Pilih Stesen",
        station_options,
        key="rainfall_extreme_station"
    )
    
    station_rainfall_df = (
        highest_daily_df[
            highest_daily_df["Station"]
            == selected_station_rainfall
        ]
        .copy()
        .sort_values(
            "Rainfall (mm)",
            ascending=False
        )
        .reset_index(drop=True)
    )
    
    # ========================================================
    # SUB TABS
    # ========================================================

    rainfall_tabs = st.tabs([
        "🌧️ Rekod Tertinggi",
        "🏆 Top 10 Tertinggi",
        "📅 Maximum Mengikut Tahun"
    ])

    # ========================================================
    # TAB 1 — REKOD TERTINGGI
    # ========================================================
    
    with rainfall_tabs[0]:
    
        st.subheader(
            "🌧️ Rekod Hujan Harian Tertinggi"
        )
    
        highest_row = (
            station_rainfall_df
            .iloc[0]
        )
    
        highest_value = (
            highest_row["Rainfall (mm)"]
        )
    
        highest_date = (
            highest_row["Date"]
        )
    
        highest_station = (
            highest_row["Station"]
        )
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.metric(
                "🌧️ Hujan Tertinggi",
                f"{highest_value:.2f} mm"
            )
    
        with col2:
            st.metric(
                "📅 Tarikh",
                highest_date.strftime("%d/%m/%Y")
            )
    
        st.markdown("---")
    
        record_table = pd.DataFrame({
            "Perkara": [
                "Hujan Harian",
                "Tarikh",
                "Tahun",
                "Bulan",
                "Hari"
            ],
            "Nilai": [
                f"{highest_value:.2f} mm",
                highest_date.strftime("%d/%m/%Y"),
                highest_date.year,
                highest_date.strftime("%B"),
                highest_date.day
            ]
        })
    
        st.dataframe(
            record_table,
            use_container_width=True,
            hide_index=True
        )
        # ====================================================
        # DOWNLOAD
        # ====================================================
        
        csv_record = (
            record_table
            .to_csv(index=False)
            .encode("utf-8-sig")
        )
        
        st.download_button(
            "⬇️ Download Rekod Tertinggi",
            data=csv_record,
            file_name=(
                f"highest_daily_rainfall_record_"
                f"{YEAR_RANGE_TEXT}.csv"
            ),
            mime="text/csv",
            key="download_rainfall_record"
        )
    # ========================================================
    # TAB 2 — TOP 10 TERTINGGI
    # ========================================================
    
    with rainfall_tabs[1]:
    
        st.subheader(
            "🏆 Top 10 Hujan Harian Tertinggi"
        )
    
        top10_data = (
            station_rainfall_df
            .sort_values(
                "Rainfall (mm)",
                ascending=False
            )
            .head(10)
            .copy()
        )
    
        top10_data["Rank"] = range(
            1,
            len(top10_data) + 1
        )
    
        display_top10 = top10_data[
            [
                "Rank",
                "Date",
                "Rainfall (mm)"
            ]
        ].copy()
    
        display_top10 = display_top10.rename(
            columns={
                "Rank": "Kedudukan",
                "Date": "Tarikh",
                "Rainfall (mm)": "Hujan Harian (mm)"
            }
        )
    
        display_top10["Tarikh"] = (
            pd.to_datetime(
                display_top10["Tarikh"]
            )
            .dt.strftime("%d-%m-%Y")
        )
    
        display_top10["Hujan Harian (mm)"] = (
            display_top10["Hujan Harian (mm)"]
            .round(2)
        )
    
        st.dataframe(
            display_top10,
            use_container_width=True,
            hide_index=True
        )
    
        # ====================================================
        # GRAPH
        # ====================================================
    
        fig, ax = plt.subplots(
            figsize=(14, 8)
        )
    
        plot_data = top10_data.sort_values(
            "Rainfall (mm)",
            ascending=True
        )
    
        bars = ax.barh(
            range(len(plot_data)),
            plot_data["Rainfall (mm)"]
        )
    
        ax.set_yticks(
            range(len(plot_data))
        )
    
        ax.set_yticklabels(
            [
                date.strftime("%d-%m-%Y")
                for date in plot_data["Date"]
            ]
        )
    
        ax.set_xlabel(
            "Hujan Harian (mm)"
        )
    
        ax.set_title(
            f"Top 10 Hujan Harian Tertinggi\n"
            f"Stesen: {selected_station_rainfall} | "
            f"{YEAR_RANGE_TEXT}",
            fontsize=16,
            fontweight="bold"
        )
    
        ax.grid(
            True,
            axis="x",
            linestyle="--",
            alpha=0.4
        )
    
        for i, value in enumerate(
            plot_data["Rainfall (mm)"]
        ):
            ax.text(
                value + 1,
                i,
                f"{value:.1f} mm",
                va="center",
                fontsize=9,
                fontweight="bold"
            )
    
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
        # ====================================================
        # DOWNLOAD GRAF PNG
        # ====================================================
        
        img = io.BytesIO()
        
        fig.savefig(
            img,
            format="png",
            dpi=300,
            bbox_inches="tight"
        )
        
        img.seek(0)
        
        st.download_button(
            "🖼️ Download Graf PNG",
            data=img,
            file_name=(
                f"top10_highest_daily_rainfall_"
                f"{YEAR_RANGE_TEXT}.png"
            ),
            mime="image/png",
            key="download_rainfall_top10_png"
        )

        plt.close(fig)
    
        # ====================================================
        # DOWNLOAD
        # ====================================================
    
        csv_top10 = (
            display_top10
            .to_csv(index=False)
            .encode("utf-8-sig")
        )
    
        st.download_button(
            "⬇️ Download Top 10",
            data=csv_top10,
            file_name=(
                f"top10_highest_daily_rainfall_"
                f"{YEAR_RANGE_TEXT}.csv"
            ),
            mime="text/csv",
            key="download_rainfall_top10"
        )
    # ========================================================
    # TAB 3 — MAXIMUM MENGIKUT TAHUN
    # ========================================================
    
    with rainfall_tabs[2]:
    
        st.subheader(
            "📅 Hujan Harian Maximum Mengikut Tahun"
        )
    
        annual_max_idx = (
            station_rainfall_df
            .groupby("Year")["Rainfall (mm)"]
            .idxmax()
        )
    
        annual_max = (
            station_rainfall_df
            .loc[
                annual_max_idx,
                [
                    "Year",
                    "Date",
                    "Station",
                    "Rainfall (mm)"
                ]
            ]
            .copy()
            .sort_values("Year")
        )
    
        annual_max_display = (
            annual_max[
                [
                    "Year",
                    "Date",
                    "Rainfall (mm)"
                ]
            ]
            .rename(
                columns={
                    "Year": "Tahun",
                    "Date": "Tarikh",
                    "Rainfall (mm)": "Maximum (mm)"
                }
            )
            .reset_index(drop=True)
        )
    
        annual_max_display["Tarikh"] = (
            pd.to_datetime(
                annual_max_display["Tarikh"]
            )
            .dt.strftime("%d/%m/%Y")
        )
    
        annual_max_display[
            "Maximum (mm)"
        ] = annual_max_display[
            "Maximum (mm)"
        ].round(2)
    
        st.dataframe(
            annual_max_display,
            use_container_width=True,
            hide_index=True
        )
    
        # ----------------------------------------------------
        # GRAPH
        # ----------------------------------------------------
    
        fig, ax = plt.subplots(
            figsize=(FIG_WIDTH, FIG_HEIGHT)
        )
    
        bars = ax.bar(
            annual_max["Year"].astype(str),
            annual_max["Rainfall (mm)"],
            edgecolor="black",
            linewidth=0.8
        )
    
        for bar, value in zip(
            bars,
            annual_max["Rainfall (mm)"]
        ):
    
            ax.text(
                bar.get_x()
                + bar.get_width() / 2,
                bar.get_height() + 2,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold"
            )
    
        ax.set_title(
            f"Maximum Daily Rainfall Mengikut Tahun\n"
            f"Stesen: {selected_station_rainfall} | "
            f"{YEAR_RANGE_TEXT}",
            fontsize=16,
            fontweight="bold"
        )
    
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Maximum Daily Rainfall (mm)")
    
        ax.grid(
            True,
            axis="y",
            linestyle="--",
            alpha=0.4
        )
    
        plt.xticks(rotation=45)
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
        
        img = io.BytesIO()
        
        fig.savefig(
            img,
            format="png",
            dpi=300,
            bbox_inches="tight"
        )
        
        img.seek(0)
        
        st.download_button(
            "🖼️ Download Graf PNG",
            data=img,
            file_name=(
                f"annual_maximum_daily_rainfall_"
                f"{YEAR_RANGE_TEXT}.png"
            ),
            mime="image/png",
            key="download_rainfall_annual_max_png"
        )

        plt.close(fig)
        # ====================================================
        # DOWNLOAD
        # ====================================================
        
        csv_annual = (
            annual_max_display
            .to_csv(index=False)
            .encode("utf-8-sig")
        )
        
        st.download_button(
            "⬇️ Download Maximum Mengikut Tahun",
            data=csv_annual,
            file_name=(
                f"annual_maximum_daily_rainfall_"
                f"{YEAR_RANGE_TEXT}.csv"
            ),
            mime="text/csv",
            key="download_rainfall_annual_max"
        )
# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("🌧️ Rainfall Data Analysis|\n")
