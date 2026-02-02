from sqlmodel import SQLModel, create_engine
import os

sqlite_file_name = "focuspipe.db"
base_dir = os.getcwd()
database_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_name)}"

engine = create_engine(database_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
	"""Cria as tabelas no banco de dados se elas não existirem."""
	SQLModel.metadata.create_all(engine)
