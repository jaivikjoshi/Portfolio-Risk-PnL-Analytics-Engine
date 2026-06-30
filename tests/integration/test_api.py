from __future__ import annotations


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seed_and_report_endpoints(client):
    seed = client.post("/api/v1/ingestion/seed")
    assert seed.status_code == 200
    assert len(seed.json()) == 6

    validation = client.post("/api/v1/validation/run")
    assert validation.status_code == 200
    assert validation.json()["status"] == "completed"

    positions = client.get("/api/v1/portfolios/P_MAIN/positions?as_of=2026-01-10")
    assert positions.status_code == 200
    body = positions.json()
    assert body["portfolio_id"] == "P_MAIN"
    assert len(body["positions"]) == 5

    pnl = client.get("/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10")
    assert pnl.status_code == 200
    pnl_body = pnl.json()
    assert pnl_body["realized_pnl"] == 344.6
    assert pnl_body["total_pnl"] > pnl_body["realized_pnl"]

    fifo = client.get(
        "/api/v1/portfolios/P_MAIN/pnl?start_date=2026-01-01&end_date=2026-01-10&cost_method=fifo"
    )
    assert fifo.status_code == 200
    assert fifo.json()["realized_pnl"] != pnl_body["realized_pnl"]

    exposure = client.get("/api/v1/portfolios/P_MAIN/exposures?as_of=2026-01-10&group_by=sector")
    assert exposure.status_code == 200
    assert exposure.json()["total_market_value"] > 0

    returns = client.get("/api/v1/portfolios/P_MAIN/returns?start_date=2026-01-02&end_date=2026-01-10")
    assert returns.status_code == 200
    assert len(returns.json()["returns"]) == 9

    risk = client.get("/api/v1/portfolios/P_MAIN/risk?start_date=2026-01-02&end_date=2026-01-10")
    assert risk.status_code == 200
    assert risk.json()["annualized_volatility"] is not None

    benchmark = client.get(
        "/api/v1/portfolios/P_MAIN/benchmark?benchmark_id=SPY&start_date=2026-01-02&end_date=2026-01-10"
    )
    assert benchmark.status_code == 200
    assert benchmark.json()["observations"] == 9

    snapshots = client.post(
        "/api/v1/portfolios/P_MAIN/snapshots?start_date=2026-01-02&end_date=2026-01-10"
    )
    assert snapshots.status_code == 200
    assert snapshots.json()["snapshots_created"] == 9

    dashboard = client.get("/dashboard/P_MAIN?start_date=2026-01-02&as_of=2026-01-10")
    assert dashboard.status_code == 200
    assert "Risk Dashboard" in dashboard.text
