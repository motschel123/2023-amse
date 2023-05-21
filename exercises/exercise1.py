import pandas as pd
from sqlalchemy import create_engine

# URL of the CSV data
data_url = "https://opendata.rhein-kreis-neuss.de/api/v2/catalog/datasets/rhein-kreis-neuss-flughafen-weltweit/exports/csv"

df = pd.read_csv(data_url, sep=";")

# Create the SQLAlchemy engine
engine = create_engine("sqlite:///airports.sqlite")

# Write the DataFrame to the SQLite database
df.to_sql("airports", engine, if_exists="replace", index=False)
