async def test_liveness(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


async def test_readiness_reports_components(client):
    """Readiness must report per-component status; redis may be absent in unit CI."""
    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    components = {c["component"] for c in body["checks"]}
    assert {"postgres", "redis"} <= components
