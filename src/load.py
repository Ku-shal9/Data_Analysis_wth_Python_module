## load script remaining
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# loading the configuration file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env" / ".env")


CSV_PATH = BASE_DIR / "dataset" / "cleaned_asteroids.csv"

# reading the CSV file using above CSV_PATH
df = pd.read_csv(CSV_PATH)

# defnining the postgres connection
def get_engine():
    DATABASE_URL = (
        f"postgresql+psycopg2://{os.environ['DB_USER']}:"
        f"{os.environ['DB_PASSWORD']}@"
        f"{os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('DB_PORT', '5432')}/"
        f"{os.environ['DB_NAME']}"
    )

    engine = create_engine(DATABASE_URL)
    return engine

# loading the data
def load_data():
    engine = get_engine()
    
    # asteroids table
    df_asteroids = df[[
        "spkid", "full_name", "class", "orbit_id", "neo_flag", "pha_flag", "orbit_shape"
    ]]
    df_asteroids.to_sql("asteroids", engine, if_exists="replace", index=False)

    # orbital_parameters table
    df_orbital = df[[
        "spkid", "epoch", "eccentricity", "semimajor_axis", "perihelion_distance",
        "orbital_period_years", "inclination", "longitude_of_ascending_node",
        "argument_of_perihelion", "mean_anomaly", "minimum_orbit_intersection_distance"
    ]]
    df_orbital.to_sql("orbital_parameters", engine, if_exists="replace", index=False)
		
    # physical_properties table
    df_physical = df[[
        "spkid", "absolute_magnitude", "diameter", "albedo", "rotation_period"
    ]]
    df_physical.to_sql("physical_properties", engine, if_exists="replace", index=False)
    
    # class_summary table
    df_summary = (
        df.groupby("class")
          .agg(
              asteroid_count=("spkid", "count"),
              average_diameter=("diameter", "mean"),
              median_diameter=("diameter", "median"),
              average_albedo=("albedo", "mean")
          )
          .reset_index()
    )
    df_summary.to_sql("class_summary", engine, if_exists="replace", index=False)

    # orbit_classes table
    df_classes = df[["class"]].drop_duplicates().rename(columns={"class": "class_code"})
    df_classes.to_sql("orbit_classes", engine, if_exists="replace", index=False)

    print("Tables has been successfully created!")

if __name__ == "__main__":
    load_data()
