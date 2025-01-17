import os
import pandas as pd

from fastapi import FastAPI, File, UploadFile
from azure.storage.blob import BlobServiceClient

from .logging_config import get_logger

app = FastAPI(title="Data Upload Service")
logger = get_logger("data-upload")

# Azure config
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
    Uploads a CSV file to Azure Blob Storage and logs the operation to Elasticsearch.
    """
    try:
        local_path = f"/tmp/{file.filename}"
        with open(local_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Upload to Azure
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=file.filename
        )
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        # Simple CSV analysis
        df = pd.read_csv(local_path)
        total_sales = float(df["Amount"].sum())
        top_product = str(df.groupby("Product")["Amount"].sum().idxmax())

        logger.info({
            "event": "FileUploaded",
            "filename": file.filename,
            "total_sales": total_sales,
            "top_product": top_product
        })

        return {
            "filename": file.filename,
            "insights": {
                "total_sales": total_sales,
                "top_product": top_product
            },
            "location": blob_client.url
        }
    except Exception as e:
        logger.error({
            "event": "UploadError",
            "error": str(e)
        })
        return {"error": str(e)}
