import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from services.data_query.main import app

client = TestClient(app)

@patch("services.data_query.main.blob_service_client")
def test_query_sales_data(mock_blob_service):
    mock_blob_client = MagicMock()
    mock_blob_service.get_blob_client.return_value = mock_blob_client
    fake_csv = b"Product,Amount,Date\nWidgetA,100,2024-01-01\nWidgetB,200,2024-01-02\n"
    mock_blob_client.download_blob.return_value.readall.return_value = fake_csv

    response = client.get("/query/test.csv?start_date=2024-01-01&end_date=2024-01-02")
    assert response.status_code == 200
    json_data = response.json()
    assert "filename" in json_data
    assert json_data["total_sales"] == 300.0
