import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB", "medtriage")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

query = """
SELECT
    symptoms_diseases AS "SYMPTOMS/DISEASES",
    emergency_intensity AS "EMERGENCY INTENSITY",
    clinical_non_clinical AS "CLINICAL/NON CLINICAL",
    classification AS "CLASSIFICATION",
    category AS "CATEGORY"
FROM main
ORDER BY symptoms_diseases;
"""

df = pd.read_sql_query(query, engine)

df.to_excel("Dataset.xlsx", index=False)

print("Dataset.xlsx created successfully!")
print(f"Rows exported: {len(df)}")
print("Columns:", list(df.columns))