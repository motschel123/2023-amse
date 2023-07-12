
import urllib.request
import zipfile
import pandas as pd
import sqlalchemy

data_url = "https://gtfs.rhoenenergie-bus.de/GTFS.zip"
data_file = "stops.txt"
# Download the file using urllib.request.urlretrieve
filename, headers = urllib.request.urlretrieve(data_url)

# Unzip the file using zipfile.ZipFile
with zipfile.ZipFile(filename, 'r') as zip_ref:
    zip_ref.extract(data_file)

# select only relevant columns
relevant_columns = {
    "stop_id": int,
    "stop_name": str,
    "stop_lat": float,
    "stop_lon": float,
    "zone_id": int,
}

# load as pandas dataframe
df = pd.read_csv(data_file, encoding="utf-8", sep=',', usecols=relevant_columns.keys(), dtype=relevant_columns)

# filter dataframe
df = df.dropna()
df = df[df["zone_id"] == 2001]
df = df[(-90 <= df["stop_lat"]) & (df["stop_lat"] <= 90)]
df = df[(-90 <= df["stop_lon"]) & (df["stop_lon"] <= 90)]

# save df as sqlite database
engine = sqlalchemy.create_engine("sqlite:///gtfs.sqlite")
df.to_sql("stops", engine, if_exists="replace", index=False)