import logging
import os

from fastapi import FastAPI, File, UploadFile
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

@app.post("/upload")
async def upload_sales_data(file: UploadFile = File(...)):
    """
    Upload a CSV file and compute rv sales insights (total sales, top product).
    Stores the CSV in azure blob.
    """
    try:
        # Save locally to tmp
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=file.filename
        )
        with open(file_location, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logger.info(f"File {file.filename} uploaded to Azure Blob Storage.")

        # process csv
        df = pd.read_csv(file_location)
        total_sales = df["Amount"].sum()
        top_product = df.groupby("Product")["Amount"].sum().idxmax()

        insights = {
            "total_sales": float(total_sales),
            "top_product": str(top_product),
        }

        logger.info(f"Insights for {file.filename}: {insights}")

        return {
            "filename": file.filename,
            "insights": insights,
            "location": blob_client.url
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        return {"error": str(e)}
