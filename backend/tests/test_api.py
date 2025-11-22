"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "database" in data


def test_create_report(client: TestClient):
    """Test creating a new report."""
    response = client.post(
        "/api/reports",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["status"] == "pending"
    assert "id" in data


def test_create_report_invalid_url(client: TestClient):
    """Test creating a report with invalid URL."""
    response = client.post(
        "/api/reports",
        json={"url": "not-a-valid-url"}
    )
    assert response.status_code == 422  # Validation error


def test_list_reports(client: TestClient):
    """Test listing all reports."""
    # Create a report first
    client.post("/api/reports", json={"url": "https://example.com"})
    
    response = client.get("/api/reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_report_by_id(client: TestClient):
    """Test getting a specific report."""
    # Create a report
    create_response = client.post(
        "/api/reports",
        json={"url": "https://example.com"}
    )
    report_id = create_response.json()["id"]
    
    # Get the report
    response = client.get(f"/api/reports/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["url"] == "https://example.com"


def test_get_report_not_found(client: TestClient):
    """Test getting a non-existent report."""
    response = client.get("/api/reports/99999")
    assert response.status_code == 404


def test_delete_report(client: TestClient):
    """Test deleting a report."""
    # Create a report
    create_response = client.post(
        "/api/reports",
        json={"url": "https://example.com"}
    )
    report_id = create_response.json()["id"]
    
    # Delete the report
    response = client.delete(f"/api/reports/{report_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/reports/{report_id}")
    assert get_response.status_code == 404
