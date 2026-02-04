import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_read_tasks():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/tasks")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

        if len(data) > 0:
            assert "id" in data[0]

@pytest.mark.asyncio
async def test_delete_task():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        new_task = {"title": "Delete Me", "description": "I will be deleted"}
        create_response = await ac.post("/tasks/", json=new_task)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        delete_response = await ac.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 204

        check_response = await ac.get(f"/tasks/{task_id}/single")
        assert check_response.status_code == 404
        assert check_response.json()["detail"] == "Task not found"