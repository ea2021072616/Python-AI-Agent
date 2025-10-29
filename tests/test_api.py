"""
Tests básicos para el microservicio
"""
import pytest
from fastapi.testclient import TestClient
from app import create_app

client = TestClient(create_app())


def test_health_check():
    """Test del endpoint de health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data


def test_info_endpoint():
    """Test del endpoint de información"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Arludent AI Microservice"


def test_chat_endpoint():
    """Test básico del endpoint de chat"""
    payload = {
        "message": "Hola",
        "user_id": 1
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "session_id" in data


def test_chat_empty_message():
    """Test de validación de mensaje vacío"""
    payload = {
        "message": "",
        "user_id": 1
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 422  # Validation error
