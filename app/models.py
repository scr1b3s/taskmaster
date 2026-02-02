from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


# 1. Tabela de Domínios (Macro-áreas)
class Domain(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	name: str
	color_hex: str
	tasks: List["Task"] = Relationship(back_populates="domain")


# 2. Tabela de Tarefas (Espelho Inteligente do GTasks)
class Task(SQLModel, table=True):
	google_task_id: str = Field(primary_key=True)
	title: str
	status: str = "needsAction"

	# Hierarquia
	parent_id: Optional[str] = Field(default=None, foreign_key="task.google_task_id")

	# Triagem
	domain_id: Optional[int] = Field(default=None, foreign_key="domain.id")
	is_triaged: bool = Field(default=False)

	created_at: datetime = Field(default_factory=datetime.utcnow)

	# Relacionamentos
	domain: Optional[Domain] = Relationship(back_populates="tasks")
	time_entries: List["TimeEntry"] = Relationship(back_populates="task")
	interruptions: List["Interruption"] = Relationship(back_populates="task")


# 3. Tabela de Entradas de Tempo (O Pomodoro Real)
class TimeEntry(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	task_id: str = Field(foreign_key="task.google_task_id")

	start_time: datetime
	end_time: Optional[datetime] = None
	duration_seconds: int = 0

	completed_cycle: bool = False

	task: Optional[Task] = Relationship(back_populates="time_entries")


# 4. Tabela de Interrupções (O "Porquê" da pausa)
class Interruption(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	task_id: str = Field(foreign_key="task.google_task_id")

	occurred_at: datetime = Field(default_factory=datetime.utcnow)
	reason: str  # Ex: "Biológico", "Família", "Outros"
	notes: Optional[str] = None

	task: Optional[Task] = Relationship(back_populates="interruptions")
