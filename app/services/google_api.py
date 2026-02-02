import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlmodel import Session, select
from app.models import Task
from app.database import engine

SCOPES = ["https://www.googleapis.com/auth/tasks"]


def get_service():
	"""Autentica e retorna o cliente da API."""
	creds = None
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)

	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
			creds = flow.run_local_server(port=0)

		with open("token.json", "w") as token:
			token.write(creds.to_json())

	return build("tasks", "v1", credentials=creds)


def sync_tasks_to_db():
	"""ETL: Puxa tarefas do Google e salva/atualiza no SQLite."""
	service = get_service()

	results = service.tasklists().list(maxResults=10).execute()
	task_lists = results.get("items", [])

	total_synced = 0

	with Session(engine) as session:
		for task_list in task_lists:
			tasks_result = (
				service.tasks()
				.list(tasklist=task_list["id"], showHidden=True, maxResults=100)
				.execute()
			)

			tasks = tasks_result.get("items", [])

			for t in tasks:
				statement = select(Task).where(Task.google_task_id == t["id"])
				existing_task = session.exec(statement).first()

				if existing_task:
					existing_task.title = t["title"]
					existing_task.status = t["status"]
					existing_task.parent_id = t.get("parent")
					session.add(existing_task)
				else:
					new_task = Task(
						google_task_id=t["id"],
						title=t["title"],
						status=t["status"],
						parent_id=t.get("parent"),
						domain_id=None,
						is_triaged=False,
					)
					session.add(new_task)

				total_synced += 1

		session.commit()
		return {"status": "success", "synced_count": total_synced}


if __name__ == "__main__":
	print("Rodando Sync Manual...")
	resultado = sync_tasks_to_db()
	print(f"Sync concluído! Tarefas processadas: {resultado['synced_count']}")
