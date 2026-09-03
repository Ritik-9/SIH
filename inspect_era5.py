import xarray as xr

accum = xr.open_dataset(
    "data/era5/data_stream-oper_stepType-accum.nc"
)

instant = xr.open_dataset(
    "data/era5/data_stream-oper_stepType-instant.nc"
)

print("\n========== INSTANT DATA ==========")
print(instant)

print("\n========== ACCUMULATED DATA ==========")
print(accum)

print("\n========== INSTANT VARIABLES ==========")
print(instant.data_vars)

print("\n========== ACCUM VARIABLES ==========")
print(accum.data_vars)

print("\n========== COORDINATES ==========")
print(instant.coords)

print("\n========== UNITS ==========")

for var in ["t2m", "d2m", "u10", "v10", "sp"]:
    if var in instant:
        print(f"{var}: {instant[var].attrs}")

if "ssrd" in accum:
    print(f"ssrd: {accum['ssrd'].attrs}")