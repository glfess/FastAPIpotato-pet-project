import json

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response

from app.api.v1 import tasks
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.core.database import get_db

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class mod_JSON_Response(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(",", ":"),
        ).encode("utf-8")

app = FastAPI(
    title="FastAPI",
    description="FastAPI",
    version="0.1.0",
)

app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])

app.mount("/static", StaticFiles(directory="/"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

@app.post("/tasks/", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=data.title, description=data.description)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    query = select(Task).where(Task.is_deleted == False).order_by(Task.id)
    results = await db.execute(query)
    tasks = results.scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks

@app.get("/")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    query = select(Task).where(Task.is_deleted == False).order_by(Task.id)
    results = await db.execute(query)
    tasks = results.scalars().all()

    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    data = {
        "status": "online",
        "total_tasks": len(tasks),
        "my_todo_list": [
            {
                "id": task.id,
                "title": task.title,
                "is_completed": task.is_completed,
                "created_at": task.created_at,
                "description": task.description
            } for task in tasks
        ]
    }
    return mod_JSON_Response(content=jsonable_encoder(data))

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)

    return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()

@app.patch("/tasks/{task_id}/delete")
async def soft_delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task or task.is_deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_deleted = True
    await db.commit()
    return {"deleted": True, "task_id": task_id}

@app.patch("/tasks/{task_id}/restore")
async def soft_restore_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task or not task.is_deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_deleted = False
    await db.commit()
    return {"deleted": False, "task_id": task_id}

@app.get("/tasks/{task_id}/single")
async def get_single_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(Task.id == task_id).where(Task.is_deleted == False)
    result = await db.execute(query)
    task = result.scalars().all()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")


    return task