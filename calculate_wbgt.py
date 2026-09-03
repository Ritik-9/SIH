import xarray as xr
import numpy as np
import pandas as pd
from pywbgt import wbgt
from metpy.units import units


# ============================================================
# CONFIGURATION
# ============================================================

YEARS = [2020, 2021, 2022, 2023, 2024]

LAT = 28.50
LON = 77.25

DATA_DIR = "data/era5"


# ============================================================
# RELATIVE HUMIDITY
# ============================================================

def relative_humidity(temp, dewpoint):

    a = 17.625
    b = 243.04

    rh = 100 * (
        np.exp((a * dewpoint) / (b + dewpoint)) /
        np.exp((a * temp) / (b + temp))
    )

    return rh


# ============================================================
# WBGT RISK CLASSIFICATION
# ============================================================

def classify_heat_stress(wbgt_value):

    if wbgt_value < 23:
        return "Low"

    elif wbgt_value < 25:
        return "Elevated"

    elif wbgt_value < 28:
        return "Moderate"

    elif wbgt_value < 30:
        return "High"

    elif wbgt_value < 33:
        return "Very High"

    else:
        return "Extreme"


# ============================================================
# DAILY RISK CLASSIFICATION
# ============================================================

def classify_daily_risk(wbgt_value):

    if wbgt_value < 23:
        return "Low"

    elif wbgt_value < 25:
        return "Elevated"

    elif wbgt_value < 28:
        return "Moderate"

    elif wbgt_value < 30:
        return "High"

    elif wbgt_value < 33:
        return "Very High"

    else:
        return "Extreme"


# ============================================================
# STORE DAILY DATA FROM ALL YEARS
# ============================================================

all_daily_data = []


# ============================================================
# PROCESS EACH YEAR
# ============================================================

for year in YEARS:

    print("\n" + "=" * 60)
    print(f"PROCESSING YEAR: {year}")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. LOAD ERA5 DATA
    # --------------------------------------------------------

    accum_path = (
        f"{DATA_DIR}/{year}/"
        "data_stream-oper_stepType-accum.nc"
    )

    instant_path = (
        f"{DATA_DIR}/{year}/"
        "data_stream-oper_stepType-instant.nc"
    )

    print("Loading ERA5 data...")

    accum = xr.open_dataset(accum_path)
    instant = xr.open_dataset(instant_path)


    # --------------------------------------------------------
    # 2. SELECT DELHI GRID POINT
    # --------------------------------------------------------

    instant_delhi = instant.sel(
        latitude=LAT,
        longitude=LON
    )

    accum_delhi = accum.sel(
        latitude=LAT,
        longitude=LON
    )


    # --------------------------------------------------------
    # 3. CREATE DATAFRAME
    # --------------------------------------------------------

    df = instant_delhi.to_dataframe().reset_index()

    df["ssrd"] = accum_delhi["ssrd"].values


    # --------------------------------------------------------
    # 4. UNIT CONVERSIONS
    # --------------------------------------------------------

    # Kelvin -> Celsius

    df["temperature_C"] = (
        df["t2m"] - 273.15
    )

    df["dewpoint_C"] = (
        df["d2m"] - 273.15
    )


    # Wind speed

    df["wind_speed"] = np.sqrt(
        df["u10"]**2 +
        df["v10"]**2
    )


    # Solar radiation
    # J/m² -> W/m²

    df["solar_radiation"] = (
        df["ssrd"] / 3600
    )


    # --------------------------------------------------------
    # 5. RELATIVE HUMIDITY
    # --------------------------------------------------------

    df["relative_humidity"] = relative_humidity(
        df["temperature_C"],
        df["dewpoint_C"]
    )


    # --------------------------------------------------------
    # 6. PREPARE DATA FOR pywbgt
    # --------------------------------------------------------

    temp_air = (
        df["temperature_C"].values + 273.15
    ) * units.kelvin

    temp_dew = (
        df["dewpoint_C"].values + 273.15
    ) * units.kelvin

    wind = (
        df["wind_speed"].values
        * units.meter
        / units.second
    )

    solar = (
        df["solar_radiation"].values
        * units.watt
        / units.meter**2
    )

    pressure = (
        instant_delhi["sp"].values
        * units.pascal
    )

    datetime = pd.DatetimeIndex(
        df["valid_time"]
    )

    lat_array = np.full(
        len(df),
        LAT
    )

    lon_array = np.full(
        len(df),
        LON
    )


    # --------------------------------------------------------
    # 7. CALCULATE WBGT
    # --------------------------------------------------------

    print("Calculating hourly WBGT...")

    result = wbgt(
        datetime=datetime,
        lat=lat_array,
        lon=lon_array,
        solar=solar,
        pres=pressure,
        temp_air=temp_air,
        temp_dew=temp_dew,
        speed=wind,
        method="liljegren"
    )


    wbgt_values = result[3]

    df["WBGT_C"] = (
        wbgt_values.magnitude
    )


    # --------------------------------------------------------
    # 8. HOURLY HEAT STRESS
    # --------------------------------------------------------

    df["heat_stress"] = (
        df["WBGT_C"]
        .apply(classify_heat_stress)
    )


    # --------------------------------------------------------
    # 9. CREATE DATE
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["valid_time"]
    ).dt.date


    # --------------------------------------------------------
    # 10. DAILY INDICATORS
    # --------------------------------------------------------

    daily = df.groupby("date").agg(

        max_WBGT=("WBGT_C", "max"),

        mean_WBGT=("WBGT_C", "mean"),

        max_temperature=(
            "temperature_C",
            "max"
        ),

        mean_temperature=(
            "temperature_C",
            "mean"
        ),

        max_humidity=(
            "relative_humidity",
            "max"
        ),

        mean_humidity=(
            "relative_humidity",
            "mean"
        ),

        max_dewpoint=(
            "dewpoint_C",
            "max"
        ),

        mean_dewpoint=(
            "dewpoint_C",
            "mean"
        ),

        max_wind_speed=(
            "wind_speed",
            "max"
        ),

        mean_wind_speed=(
            "wind_speed",
            "mean"
        ),

        max_solar_radiation=(
            "solar_radiation",
            "max"
        ),

        mean_solar_radiation=(
            "solar_radiation",
            "mean"
        ),

        mean_pressure=(
            "sp",
            "mean"
        )

    ).reset_index()


    # --------------------------------------------------------
    # 11. HIGH WBGT HOURS
    # --------------------------------------------------------

    high_hours = (
        df[df["WBGT_C"] >= 30]
        .groupby("date")
        .size()
        .rename("high_WBGT_hours")
    )


    daily = daily.merge(
        high_hours,
        on="date",
        how="left"
    )


    daily["high_WBGT_hours"] = (
        daily["high_WBGT_hours"]
        .fillna(0)
    )


    # --------------------------------------------------------
    # 12. DAILY RISK LEVEL
    # --------------------------------------------------------

    daily["daily_risk_level"] = (
        daily["max_WBGT"]
        .apply(classify_daily_risk)
    )


    # --------------------------------------------------------
    # 13. HEATWAVE DAY
    # --------------------------------------------------------

    daily["heatwave_day"] = (
        daily["high_WBGT_hours"] >= 3
    )


    # --------------------------------------------------------
    # 14. ADD YEAR
    # --------------------------------------------------------

    daily["year"] = year


    # --------------------------------------------------------
    # 15. STORE YEAR
    # --------------------------------------------------------

    all_daily_data.append(daily)


    print(f"\n{year} completed.")

    print(
        f"Days processed: {len(daily)}"
    )

    print(
        f"Heatwave days: "
        f"{daily['heatwave_day'].sum()}"
    )


    # Close datasets

    instant.close()
    accum.close()


# ============================================================
# 16. COMBINE ALL YEARS
# ============================================================

print("\n" + "=" * 60)
print("COMBINING ALL YEARS")
print("=" * 60)


daily_all = pd.concat(
    all_daily_data,
    ignore_index=True
)


# Sort chronologically

daily_all["date"] = pd.to_datetime(
    daily_all["date"]
)

daily_all = daily_all.sort_values(
    "date"
).reset_index(drop=True)


# ============================================================
# 17. DAILY RISK COUNTS
# ============================================================

print("\nDAILY RISK LEVEL COUNTS:")
print(
    daily_all["daily_risk_level"]
    .value_counts()
    .reindex(
        [
            "Low",
            "Elevated",
            "Moderate",
            "High",
            "Very High",
            "Extreme"
        ],
        fill_value=0
    )
)


# ============================================================
# 18. HEATWAVE SUMMARY
# ============================================================

total_days = len(daily_all)

heatwave_days = (
    daily_all["heatwave_day"].sum()
)

max_wbgt = (
    daily_all["max_WBGT"].max()
)

max_temperature = (
    daily_all["max_temperature"].max()
)

mean_wbgt = (
    daily_all["mean_WBGT"].mean()
)


print("\nHEATWAVE SUMMARY:")
print("-" * 40)

print(
    f"Total days analyzed: {total_days}"
)

print(
    f"Heatwave days: {heatwave_days}"
)

print(
    f"Maximum WBGT: "
    f"{max_wbgt:.2f} °C"
)

print(
    f"Maximum temperature: "
    f"{max_temperature:.2f} °C"
)

print(
    f"Average daily WBGT: "
    f"{mean_wbgt:.2f} °C"
)


# ============================================================
# 19. YEAR-WISE SUMMARY
# ============================================================

print("\nYEAR-WISE SUMMARY:")
print("-" * 40)

year_summary = (
    daily_all
    .groupby("year")
    .agg(
        days=("date", "count"),
        heatwave_days=(
            "heatwave_day",
            "sum"
        ),
        max_WBGT=(
            "max_WBGT",
            "max"
        ),
        mean_WBGT=(
            "mean_WBGT",
            "mean"
        )
    )
    .reset_index()
)

print(year_summary.to_string(index=False))


# ============================================================
# 20. SAVE FINAL DATASET
# ============================================================

output_file = (
    "daily_heatwave_data.csv"
)

daily_all.to_csv(
    output_file,
    index=False
)


print(
    f"\nDaily heatwave data saved to: "
    f"{output_file}"
)


# ============================================================
# 21. VALIDATE HIGHEST WBGT VALUES
# ============================================================

print("\nHIGHEST DAILY WBGT VALUES:")
print("-" * 40)

print(
    daily_all
    .nlargest(20, "max_WBGT")[
        [
            "date",
            "year",
            "max_WBGT",
            "mean_WBGT",
            "max_temperature",
            "daily_risk_level",
            "high_WBGT_hours",
            "heatwave_day"
        ]
    ]
    .to_string(index=False)
)


print("\nPROCESSING COMPLETE!")