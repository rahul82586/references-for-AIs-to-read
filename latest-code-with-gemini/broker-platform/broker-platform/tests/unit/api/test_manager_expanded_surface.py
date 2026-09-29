"""
Unit tests for expanded MT5 Manager API endpoints:
- RouteEvaluate
- NOPLimitCheck
- LPBridgeConnect
- ABookAllocation
- MarginCheck
- ForceLiquidation
- AccountStatement
- DailySummary
"""
import pytest
from fastapi.testclient import TestClient
from api.main import create_app
from api.auth.jwt_handler import create_access_token


def test_manager_expanded_endpoints():
    app = create_app()
    client = TestClient(app)
    
    token = create_access_token({"sub": "100001", "is_manager": True})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. NOP Limit Check
    resp = client.get("/api/v1/manager/NOPLimitCheck?symbol=EURUSD&volume=10.0", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "EURUSD"
    assert "recommended_action" in data
    
    # 2. LP Bridge Connect
    resp = client.post("/api/v1/manager/LPBridgeConnect", json={
        "lp_name": "LMAX",
        "protocol": "FIX4.4",
        "target_comp_id": "LMAX_GW_01"
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONNECTED"
    
    # 3. Daily Summary Report
    resp = client.get("/api/v1/manager/DailySummary?days=3", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    
    # 4. Force Liquidation
    resp = client.post("/api/v1/manager/ForceLiquidation", json={
        "login": 744209,
        "comment": "Dealer stopout test"
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["login"] == 744209

