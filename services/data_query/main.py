import os
import io
import pandas as pd

from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
from typing import Optional
from datetime import datetime

from .logging_config import get_logger

app = FastAPI(title="Data Query Service")
logger = get_logger("data-query")

STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "your_account_name")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY", "your_account_key")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "dataflow")

blob_service_client = BlobServiceClient(
    f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=STORAGE_ACCOUNT_KEY
)

@app.get("/query/{filename}")
async def query_sales_data(filename: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Fetch a CSV from Azure Blob, optionally filter by date range, logs to Elasticsearch.
    """
    try:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=filename
        )
        blob_data = blob_client.download_blob().readall()

        df = pd.read_csv(io.BytesIO(blob_data))

        if "Amount" not in df.columns:
            logger.warning({
                "event": "MissingColumn",
                "filename": filename
            })
            return {"error": f"No 'Amount' column in {filename}"}

        if start_date and end_date and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            df = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)]

        total_sales = float(df["Amount"].sum())
        sales_by_date = {}
        if "Date" in df.columns:
            grouped = df.groupby(df["Date"].dt.date)["Amount"].sum()
            sales_by_date = {str(k): float(v) for k, v in grouped.items()}

        logger.info({
            "event": "FileQueried",
            "filename": filename,
            "total_sales": total_sales,
            "start_date": start_date,
            "end_date": end_date
        })

        return {
            "filename": filename,
            "total_sales": total_sales,
            "sales_by_date": sales_by_date
        }
    except Exception as e:
        logger.error({
            "event": "QueryError",
            "error": str(e)
        })
        return {"error": str(e)}
