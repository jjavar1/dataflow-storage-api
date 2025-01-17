import logging
import os
import io

from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "your_account_name")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY", "your_account_key")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "dataflow")

blob_service_client = BlobServiceClient(
    f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=STORAGE_ACCOUNT_KEY
)

@app.get("/query/{filename}")
async def query_sales_data(filename: str, start_date: str = None, end_date: str = None):
    """
    Fetch CSV from Azure, optionally filter by date range,
    and return sales info (total sales, sales by date).
    """
    try:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=filename
        )
        blob_data = blob_client.download_blob().readall()

        logger.info(f"File {filename} downloaded from Azure Blob Storage.")

        # Load CSV into DataFrame
        df = pd.read_csv(io.BytesIO(blob_data))

        # filter by date range
        if start_date and end_date and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            filtered_df = df[
                (df["Date"] >= pd.to_datetime(start_date)) &
                (df["Date"] <= pd.to_datetime(end_date))
            ]
        else:
            filtered_df = df

        total_sales = filtered_df["Amount"].sum() if "Amount" in filtered_df.columns else 0.0
        sales_by_date = {}
        if "Date" in filtered_df.columns:
            sales_by_date = filtered_df.groupby("Date")["Amount"].sum().to_dict()

        logger.info(f"Query insights for {filename}: total_sales={total_sales}")

        return {
            "filename": filename,
            "total_sales": float(total_sales),
            "sales_by_date": sales_by_date
        }
    except Exception as e:
        logger.error(f"Error querying file: {e}", exc_info=True)
        return {"error": str(e)}
