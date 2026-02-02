from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, Form 
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, col, desc
from app.database import create_db_and_tables, engine
from app.models import Domain, Task, TimeEntry, Interruption
from app.services.google_api import sync_tasks_to_db
from datetime import datetime

templates = Jinja2Templates(directory="app/templates")


def get_session():
	with Session(engine) as session:
		yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
	print("Startup: Inicializando banco de dados...")
	create_db_and_tables()
	yield
	print("Shutdown: Até logo!")


app = FastAPI(title="FocusPipe API", version="0.1.0", lifespan=lifespan)


@app.get("/")
def read_root(request: Request, session: Session = Depends(get_session)):
	statement = select(Task).order_by(col(Task.is_triaged), desc(Task.created_at))
	tasks = session.exec(statement).all()

	return templates.TemplateResponse(
		"index.html", {"request": request, "tasks": tasks}
	)


@app.get("/sync")
def trigger_sync():
	"""Endpoint para forçar a sincronização com o Google Tasks."""
	try:
		result = sync_tasks_to_db()
		return result
	except Exception as e:
		return {"status": "error", "detail": str(e)}


@app.post("/tasks/{task_id}/triage")
def triage_task(
	task_id: str, domain: str, request: Request, session: Session = Depends(get_session)
):
	task = session.get(Task, task_id)
	if not task:
		return HTMLResponse("Tarefa não encontrada", status_code=404)

	statement = select(Domain).where(Domain.name == domain)
	domain_obj = session.exec(statement).first()

	if not domain_obj:
		color = "#3b82f6" if domain == "Work" else "#10b981"
		domain_obj = Domain(name=domain, color_hex=color)
		session.add(domain_obj)
		session.commit()
		session.refresh(domain_obj)

	task.domain_id = domain_obj.id
	task.is_triaged = True
	session.add(task)
	session.commit()
	session.refresh(task)

	return templates.TemplateResponse(
		"fragments/badge.html", {"request": request, "task": task}
	)

@app.get("/tasks/{task_id}/select")
def select_task_for_focus(
    task_id: str, 
    request: Request,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        return HTMLResponse("Tarefa não encontrada", status_code=404)
        
    return templates.TemplateResponse("fragments/focus_panel.html", {
        "request": request, 
        "task": task
    })

# --- ENDPOINTS DO TIMER ---

@app.post("/tasks/{task_id}/start")
def start_timer(
    task_id: str, 
    request: Request,
    session: Session = Depends(get_session)
):
    statement = select(TimeEntry).where(
        TimeEntry.task_id == task_id, 
        TimeEntry.end_time == None
    )
    active_entry = session.exec(statement).first()
    
    if not active_entry:
        new_entry = TimeEntry(task_id=task_id, start_time=datetime.utcnow())
        session.add(new_entry)
        session.commit()

    return HTMLResponse("""
        <button class="secondary outline" 
                hx-post="/tasks/{task_id}/stop" 
                hx-target="this" 
                hx-swap="outerHTML"
                onclick="stopTimer()">
            ⏹ Parar Foco
        </button>
    """.replace("{task_id}", task_id))

@app.post("/tasks/{task_id}/stop")
def stop_timer(
    task_id: str, 
    request: Request,
    session: Session = Depends(get_session)
):
    statement = select(TimeEntry).where(
        TimeEntry.task_id == task_id, 
        TimeEntry.end_time == None
    )
    active_entry = session.exec(statement).first()
    
    if active_entry:
        now = datetime.utcnow()
        active_entry.end_time = now
        duration = (now - active_entry.start_time).total_seconds()
        active_entry.duration_seconds = int(duration)
        session.add(active_entry)
        session.commit()
    
    return templates.TemplateResponse("fragments/interruption_form.html", {
        "request": request, 
        "task_id": task_id
    })

@app.post("/tasks/{task_id}/log_interruption")
def log_interruption(
    task_id: str, 
    request: Request,
    reason: str = Form(...),
    notes: str = Form(None),
    session: Session = Depends(get_session)
):
    interruption = Interruption(
        task_id=task_id,
        reason=reason,
        notes=notes,
        occurred_at=datetime.utcnow()
    )
    session.add(interruption)
    session.commit()

    return HTMLResponse("""
        <button class="contrast" 
                hx-post="/tasks/{task_id}/start" 
                hx-target="this" 
                hx-swap="outerHTML"
                onclick="startTimer()">
            ▶ Iniciar Foco
        </button>
    """.replace("{task_id}", task_id))