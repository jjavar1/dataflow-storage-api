import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from services.data_upload.main import app

client = TestClient(app)

@patch("services.data_upload.main.blob_service_client")
def test_upload_sales_data(mock_blob_service):
    mock_blob_client = MagicMock()
    mock_blob_service.get_blob_client.return_value = mock_blob_client

    csv_content = b"Product,Amount,Date\nWidgetA,100,2024-01-01\n"
    response = client.post("/upload", files={"file": ("test.csv", csv_content, "text/csv")})

    assert response.status_code == 200
    json_data = response.json()
    assert "filename" in json_data
    if "error" in json_data:
        pytest.fail(json_data["error"])
    else:
        assert "insights" in json_data
        assert json_data["insights"]["total_sales"] == 100.0
