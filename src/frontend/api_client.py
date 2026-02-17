import httpx
from typing import List, Dict, Any, Optional

BASE_URL = "http://127.0.0.1:8000"

class ApiClient:
    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL)

    def get_lists(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.get("/lists")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error (get_lists): {e}")
            return []

    def create_list(self, list_id: str, name: str) -> bool:
        try:
            payload = {"id": list_id, "name": name}
            response = self.client.post("/lists", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"API Error (create_list): {e}")
            return False

    def get_tasks(self, list_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {}
            if list_id:
                params["list_id"] = list_id
            response = self.client.get("/tasks", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error (get_tasks): {e}")
            return []

    def add_task(self, task_id: str, title: str, list_id: str = "default") -> bool:
        try:
            payload = {"id": task_id, "title": title, "completed": False, "list_id": list_id}
            response = self.client.post("/tasks", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"API Error (add_task): {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        try:
            response = self.client.delete(f"/tasks/{task_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"API Error (delete_task): {e}")
            return False

    def update_task(self, task_id: str, title: str, completed: bool, list_id: str = "default") -> bool:
        try:
            # Note: We need to preserve list_id. 
            # In a real app, we might fetch first or backend handles partial updates.
            # Here, we assume the frontend knows the list_id or we just send what we have.
            # Ideally, update endpoints should be PATCH or we fetch the full object.
            # For simplicity, we trust the caller passes the right list_id or we use default.
            # Actually, to be safe, we should probably let the backend handle it or fetch first.
            # But let's assume the frontend passes the current list_id.
            payload = {"id": task_id, "title": title, "completed": completed, "list_id": list_id}
            response = self.client.put(f"/tasks/{task_id}", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"API Error (update_task): {e}")
            return False
