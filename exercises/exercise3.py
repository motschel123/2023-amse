import pandas as pd
from sqlalchemy import create_engine

# URL of the CSV data
data_url = (
    "https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"
)
# Read the CSV data into a DataFrame
# drop the first 6 rows and the last 4 rows and encode the data with iso-8859-1 to preserve the german umlauts
df = pd.read_csv(
    data_url, sep=";", encoding="iso-8859-1", engine="python", skiprows=6, skipfooter=4
)
# Rename the columns
df.columns.values[0] = "date"
df.columns.values[1] = "CIN"
df.columns.values[2] = "name"
df.columns.values[12] = "petrol"
df.columns.values[22] = "diesel"
df.columns.values[32] = "gas"
df.columns.values[42] = "electro"
df.columns.values[52] = "hybrid"
df.columns.values[62] = "plugInHybrid"
df.columns.values[72] = "others"
# Drop all other columns
keep_cols = [
    "date",
    "CIN",
    "name",
    "petrol",
    "diesel",
    "gas",
    "electro",
    "hybrid",
    "plugInHybrid",
    "others",
]

df = df[keep_cols]

# Validate the data
# Ensure that the CIN is a string and has 5 chars (leading zeros)
df["CIN"] = df["CIN"].astype(str, errors="raise").str.zfill(5)
# all other columns should be positive integers > 0

for col in keep_cols[3:]:
    df = df[df[col] != "-"]
    df[col] = df[col].astype(int, errors="raise").dropna()
    df = df[df[col] > 0]

# Create the SQLAlchemy engine
engine = create_engine("sqlite:///cars.sqlite")

# Write the DataFrame to the SQLite database
df.to_sql("cars", engine, if_exists="replace", index=False)
