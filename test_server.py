import asyncio

import httpx
import pytest
from starlette.testclient import TestClient

import server

# Deliberately fake fixtures, never usable credentials.
PROVIDER = "test-provider-" + "x" * 32
BRIDGE = "test-bridge-" + "y" * 32


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SCRAPEDO_TOKEN", PROVIDER)
    monkeypatch.setenv("MCP_AUTH_TOKEN", BRIDGE)
    return server.create_app()


def test_missing_secrets_fail_closed(monkeypatch):
    monkeypatch.delenv("SCRAPEDO_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="SCRAPEDO_TOKEN"):
        server.create_app()


def test_auth_and_mcp_discovery(app):
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.post("/mcp", json={}).status_code == 401
        headers = {"Authorization": "Bearer " + BRIDGE,
                   "Accept": "application/json, text/event-stream"}
        init = client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "test", "version": "1"}},
        })
        assert init.status_code == 200
        assert "serverInfo" in init.json()["result"]
        result = client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {},
        })
        assert result.json()["result"]["tools"][0]["name"] == "scrape_url"
        assert client.post("/mcp", headers={**headers, "Origin": "https://evil.example"}).status_code == 403
        assert client.post("/mcp", headers={**headers, "Host": "evil.example"}, json={}).status_code == 421


@pytest.mark.parametrize("url", ["file:///etc/passwd", "https://u:p@example.com",
    "http://localhost", "http://127.0.0.1", "http://[::1]", "http://169.254.169.254",
    "https://example.com:9000", "https://example.com:bad", "https://example.com\n"])
def test_private_or_invalid_destinations(url):
    with pytest.raises(server.ToolError):
        asyncio.run(server.validate_url(url))


def test_fetch_limits_costs_and_redaction(monkeypatch):
    async def valid(url):
        return url
    monkeypatch.setattr(server, "validate_url", valid)
    def handler(request):
        assert request.url.host == "api.scrape.do"
        assert request.url.scheme == "https"
        assert request.url.params["url"] == "https://example.com/?a=1&b=2"
        assert "authorization" not in request.headers
        assert request.url.params["disableRedirection"] == "true"
        return httpx.Response(200, text=PROVIDER + BRIDGE + "z" * 250000,
                              headers={"Scrape.do-Request-Cost": "10",
                                       "Scrape.do-Remaining-Credits": "990"})
    scraper = server.Scraper(PROVIDER, BRIDGE, httpx.MockTransport(handler))
    async def run():
        for _ in range(5):
            result = await scraper.fetch("https://example.com/?a=1&b=2")
            assert result["credits_used"] == 10
            assert result["credits_remaining"] == 990
            assert result["truncated"]
            assert PROVIDER not in result["content"] and BRIDGE not in result["content"]
        with pytest.raises(server.ToolError, match="Rate limit"):
            await scraper.fetch("https://example.com/?a=1&b=2")
    asyncio.run(run())


@pytest.mark.parametrize("mode", ["http_error", "timeout"])
def test_errors_never_expose_provider_secret(monkeypatch, mode):
    async def valid(url):
        return url
    monkeypatch.setattr(server, "validate_url", valid)
    def handler(request):
        if mode == "timeout":
            raise httpx.ReadTimeout(str(request.url))
        return httpx.Response(401, text=PROVIDER)
    scraper = server.Scraper(PROVIDER, BRIDGE, httpx.MockTransport(handler))
    with pytest.raises(server.ToolError) as error:
        asyncio.run(scraper.fetch("https://example.com"))
    assert PROVIDER not in str(error.value)
    assert not scraper.busy
