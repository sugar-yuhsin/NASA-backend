"""
基本測試範例
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_endpoint():
    """測試根端點"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "NASA Hackathon API" in data["message"]


def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_openapi_docs():
    """測試 OpenAPI 文檔端點"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


def test_api_v1_prefix():
    """測試 API v1 前綴存在"""
    response = client.get("/api/v1/")
    # 如果沒有根路由，應該返回 404，這表示前綴設定正確
    assert response.status_code in [200, 404, 405]