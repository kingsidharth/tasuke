import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from backend.app.main import app

@pytest.mark.asyncio
async def test_list_threads():
    transport = ASGITransport(app=app)
    async with AsyncClient(base_url="http://test", transport=transport, follow_redirects=True) as ac:
        response = await ac.get("/api/v1/threads")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_thread_detail():
    transport = ASGITransport(app=app)
    async with AsyncClient(base_url="http://test", transport=transport, follow_redirects=True) as ac:
        response = await ac.get("/api/v1/threads/1")
        assert response.status_code in (200, 404)

@pytest.mark.asyncio
async def test_pause_resume_thread():
    transport = ASGITransport(app=app)
    async with AsyncClient(base_url="http://test", transport=transport, follow_redirects=True) as ac:
        pause_resp = await ac.post("/api/v1/threads/1/pause")
        assert pause_resp.status_code in (200, 404)
        resume_resp = await ac.post("/api/v1/threads/1/resume")
        assert resume_resp.status_code in (200, 404) 