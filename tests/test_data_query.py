import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from services.data-query.main import app

client = TestClient(app)

@patch("services.data-query.main.blob_service_client.get_blob_client")
def test_query_sales_data(mock_blob_client):
    """
    Mock Azure Blob download to simulate a CSV file,
    then verify the /query endpoint.
    """
    # simulate csv
    fake_csv = b"Product,Amount,Date\nWidgetA,100,2024-01-01\nWidgetB,200,2024-01-02\n"

    mock_blob = MagicMock()
    mock_blob.download_blob.return_value.readall.return_value = fake_csv
    mock_blob_client.return_value = mock_blob

    response = client.get("/query/test.csv?start_date=2024-01-01&end_date=2024-01-02")
    assert response.status_code == 200
    json_data = response.json()

    assert "filename" in json_data
    assert "total_sales" in json_data
    assert json_data["total_sales"] == 300.0
    assert "sales_by_date" in json_data
    # The keys in sales_by_date will include datetime strings from Pandas
