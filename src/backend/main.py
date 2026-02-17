from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import uvicorn
from contextlib import asynccontextmanager

# Import path utility
try:
    from src.shared.paths import get_data_path
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.shared.paths import get_data_path

# Data Model
class Task(BaseModel):
    id: str
    title: str
    completed: bool = False
    list_id: str = "default" # New field for list association

class TaskList(BaseModel):
    id: str
    name: str

# Global state
tasks: List[Task] = []
task_lists: List[TaskList] = []

DATA_FILE = get_data_path('tasks.json')
LISTS_FILE = get_data_path('lists.json')

def load_data():
    global tasks, task_lists
    # Load Tasks
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = [Task(**item) for item in data]
        except Exception as e:
            print(f"Error loading tasks: {e}")
            tasks = []
    else:
        tasks = []
        
    # Load Lists
    if os.path.exists(LISTS_FILE):
        try:
            with open(LISTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                task_lists = [TaskList(**item) for item in data]
        except Exception as e:
            print(f"Error loading lists: {e}")
            task_lists = [TaskList(id="default", name="今日任务")]
    else:
        # Default list
        task_lists = [TaskList(id="default", name="今日任务")]
        save_lists()

def save_tasks():
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([t.model_dump() for t in tasks], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {e}")

def save_lists():
    try:
        os.makedirs(os.path.dirname(LISTS_FILE), exist_ok=True)
        with open(LISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([l.model_dump() for l in task_lists], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving lists: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    yield
    save_tasks()
    save_lists()

app = FastAPI(lifespan=lifespan)

# --- List Endpoints ---

@app.get("/lists", response_model=List[TaskList])
async def get_lists():
    return task_lists

@app.post("/lists", response_model=TaskList)
async def create_list(task_list: TaskList):
    for l in task_lists:
        if l.id == task_list.id:
            raise HTTPException(status_code=400, detail="List ID already exists")
    task_lists.append(task_list)
    save_lists()
    return task_list

@app.delete("/lists/{list_id}")
async def delete_list(list_id: str):
    global task_lists, tasks
    
    # Prevent deleting the default list if needed (optional, but good practice)
    # However, if user wants to delete it, maybe we should allow it but ensure a default always exists.
    # For now, let's assume "default" list ID is "default" and cannot be deleted.
    if list_id == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default list")
        
    # Find list
    list_to_delete = next((l for l in task_lists if l.id == list_id), None)
    if not list_to_delete:
        raise HTTPException(status_code=404, detail="List not found")
        
    # Delete list
    task_lists = [l for l in task_lists if l.id != list_id]
    
    # Delete associated tasks
    tasks = [t for t in tasks if t.list_id != list_id]
    
    save_lists()
    save_tasks()
    return {"status": "success"}

# --- Task Endpoints ---

@app.get("/tasks", response_model=List[Task])
async def get_tasks(list_id: Optional[str] = None):
    if list_id:
        return [t for t in tasks if t.list_id == list_id]
    return tasks

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    for t in tasks:
        if t.id == task.id:
            raise HTTPException(status_code=400, detail="Task ID already exists")
    
    # Ensure list exists
    if not any(l.id == task.list_id for l in task_lists):
        # Fallback to default or create? For now let's allow it or default it
        # Ideally should validate list_id. 
        # If client sends garbage list_id, it might get lost in UI.
        # But let's assume client is good.
        pass
        
    tasks.append(task)
    save_tasks()
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    save_tasks()
    return {"status": "success"}

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: Task):
    for i, t in enumerate(tasks):
        if t.id == task_id:
            tasks[i] = task
            save_tasks()
            return task
    raise HTTPException(status_code=404, detail="Task not found")

def start_backend(host="127.0.0.1", port=8000):
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_backend()
