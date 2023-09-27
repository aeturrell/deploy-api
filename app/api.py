from pathlib import Path

import pandas as pd
from fastapi import FastAPI

app = FastAPI(
    title="Deaths Data API",
    description="Get the data",
    summary="Retrieve ONS deaths data for England and Wales",
)

df = pd.read_parquet(Path("scratch/deaths_data.parquet"))
df["datetime"] = df["datetime"].astype("string[pyarrow]")
df = df.set_index("datetime")

description = (
    f"Use year and geo code to retrieve deaths data. Max year is {df['year'].max()}."
)


@app.get("/year/{year}/geo_code/{geo_code}", description=description)
async def read_item(year: int, geo_code: str):
    json_data = df.loc[
        (df["year"] == year) & (df["geo_code"] == geo_code), "deaths"
    ].to_dict()
    return {"year": year, "geo_code": geo_code, "data": json_data}
