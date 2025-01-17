# OpenFlow CSV (dataflow-storage-api)

OpenFlow CSV (name tbd) is an **open-source** microservices project that ingests CSV files, performs 'basic' data extraction, and logs service events using **Elasticsearch** and **Kibana**. I aim to extend this project’s capabilities over time, adding more complex CSV transformations and data analytics features. Was a pet project for other private projects but decided to open source and remove all licensed code.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
5. [Usage](#usage)
6. [Logs & Monitoring](#logs--monitoring)
7. [Testing](#testing)
8. [Contributing](#contributing)
9. [Roadmap](#roadmap)
10. [License](#license)

---

## Overview

OpenFlow CSV is designed for developers, data engineers, and enthusiasts who want a **modular**, **containerized** way to:
- **Upload** CSV data to the cloud (Azure Blob Storage).
- **Query** extracted data via REST APIs.
- **Send structured JSON logs** to Elasticsearch, viewable in Kibana.

We keep it **open-source** so anyone can:
- Improve existing features.
- Add new data-processing capabilities.
- Integrate with different cloud services or logging platforms.

---

## Features

- **FastAPI Microservices**: Independent data-upload and data-query services.
- **Azure Blob Storage Integration**: Real cloud storage for uploaded CSVs.
- **Logging with Elasticsearch/Kibana**: Real-time JSON logs, easy to search and visualize.
- **Docker Compose Orchestration**: Single command spin-up for all services, including Elastic.

---

## Architecture

1. **data-upload**  
   - Upload CSV files to Azure Blob Storage.
   - Optionally compute basic metrics (e.g., sum of an `Amount` column).
   - Logs ingestion events to Elasticsearch.

2. **data-query**  
   - Retrieves CSV from Azure Blob Storage.
   - Supports optional filters (e.g., date range).
   - Logs query details to Elasticsearch.

3. **Elasticsearch** (default port: 9200)  
   - Stores logs in structured JSON documents (index: `python-logs`).

4. **Kibana** (default port: 5601)  
   - Frontend for searching and visualizing logs in Elasticsearch.

---

## Getting Started

### Prerequisites
- **Docker** & **Docker Compose**  
- **Azure Storage Account** (if you want actual blob storage instead of a local mock):
  - Set these environment variables:
    ```bash
    export STORAGE_ACCOUNT_NAME="your_account_name"
    export STORAGE_ACCOUNT_KEY="your_account_key"
    export CONTAINER_NAME="csv-container"
    ```
- **Git** to clone this repository (optional if you just download ZIP).

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/OpenFlow-CSV.git
   cd OpenFlow-CSV
    ```

### Set Environment Variables:

```bash
export STORAGE_ACCOUNT_NAME="your_storage_account_name"
export STORAGE_ACCOUNT_KEY="your_storage_account_key"
export CONTAINER_NAME="csv-container"
```

### Build & Run with Docker Compose:

```bash
docker-compose up --build
```

This launches:

- data-upload (port 8001)
- data-query (port 8002)
- elasticsearch (port 9200)
- kibana (port 5601)

## Usage

1. **Upload CSV**  
   - Endpoint: `POST http://localhost:8001/upload`  
   - Example:
     ```bash
     curl -X POST "http://localhost:8001/upload" \
          -F "file=@sample.csv"
     ```
   - Response might include:
     ```json
     {
       "filename": "sample.csv",
       "insights": {
         "total_sales": 250.0,
         "top_product": "ProductA"
       },
       "location": "https://your_storage_account.blob.core.windows.net/csv-container/sample.csv"
     }
     ```

2. **Query CSV**  
   - Endpoint: `GET http://localhost:8002/query/{filename}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
   - Example:
     ```bash
     curl "http://localhost:8002/query/sample.csv?start_date=2024-01-01&end_date=2024-02-01"
     ```
   - Response might include:
     ```json
     {
       "filename": "sample.csv",
       "total_sales": 250.0,
       "sales_by_date": {
         "2024-01-01": 100.0,
         "2024-01-02": 150.0
       }
     }
     ```

---

## Logs & Monitoring

- **Elasticsearch**: http://localhost:9200  
- **Kibana**: http://localhost:5601  
  1. Visit **Kibana** and create an index pattern (e.g., `python-logs*`).  
  2. Access the **Discover** tab to see real-time logs.  
  3. Filter, visualize, and create dashboards for your logs.

Sample log document (JSON):
```json
{
  "@timestamp": "2025-01-17T12:34:56.789Z",
  "message": "{\"event\": \"FileUploaded\", \"filename\": \"sample.csv\", \"total_sales\": 250.0}",
  "logger": "data-upload",
  "level": "INFO"
}
```

## Testing
##Local Testing (without Docker):

```bash
pip install -r services/data-upload/requirements.txt
pip install -r services/data-query/requirements.txt
pip install pytest
pytest
```

## Contributing
We welcome pull requests and feature suggestions!

1. Fork this repo.
2. Create a feature branch.
3. Implement new data extraction capabilities or improvements to logging.
4. Submit a pull request.
Please open an issue if you find bugs or need support.
