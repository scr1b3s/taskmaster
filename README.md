# Taskmaster (FocusPipe)

> *A Data Engineering approach to personal productivity and dispersion control.*

**Taskmaster** (internally codenamed *FocusPipe*) is a local-first web application designed to act as an enrichment layer over **Google Tasks**. It solves the problem of context switching and "time dispersion" by forcing a strict linkage between time-tracking (Pomodoro) and specific tasks/domains.

Unlike standard to-do lists, Taskmaster treats your daily activity as a data ingestion and transformation problem, generating high-quality granular data for self-analysis.

## 🏗 Architecture & Stack

This project is built with a **"Lean & Clean"** philosophy, utilizing Server-Side Rendering (SSR) to minimize complexity and modern Python tooling for performance.

* **Package Manager:** [`uv`](https://github.com/astral-sh/uv) (Blazing fast Python package installer)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **Database:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLite)
* **Frontend:** Jinja2 (Templates) + [HTMX](https://htmx.org/) (Interactivity)
* **Styling:** [Pico.css](https://picocss.com/) (Class-less, semantic HTML)
* **Linting/Formatting:** [`ruff`](https://github.com/astral-sh/ruff) (Configured for **Tabs** indentation)

## 🚀 Key Features (MVP)

* **Google Tasks Ingestion (ETL):** Pulls tasks and subtasks from your Google account.
* **Hierarchical Triage:** Rapidly classify tasks into Domains (e.g., *Work, Personal*) with cascade inheritance (Parent -> Child).
* **Contextual Timer:** You cannot start a timer without linking it to a specific Task.
* **Dispersion Tracking:** Logs not just *time*, but *interruptions* and their reasons (e.g., "Urgency", "Procrastination").
* **Local Privacy:** All behavioral data lives in a local `focuspipe.db` SQLite file. No external servers.

## 🛠️ Installation & Setup

### Prerequisites

* Python 3.12+
* [`uv`](https://github.com/astral-sh/uv) installed.
* Google Cloud Console credentials (OAuth 2.0 Client ID) saved as `client_secret.json` (root directory).

### 1. Clone the Repository

```bash
git clone [https://github.com/scr1b3s/taskmaster.git](https://github.com/scr1b3s/taskmaster.git)
cd taskmaster

```

### 2. Install Dependencies

Using `uv`, this sets up the virtual environment and installs all requirements from `pyproject.toml`.

```bash
uv sync

```

### 3. Environment Variables

Create a `.env` file in the root directory.
*(Note: Since this runs locally, simple API keys are currently used. OpenBao integration is planned for v2).*

```bash
# .env example
GOOGLE_CLIENT_ID="your_client_id"
GOOGLE_CLIENT_SECRET="your_client_secret"
SECRET_KEY="your_random_secret_key"

```

### 4. Run the Application

This command starts the Uvicorn server with hot-reload enabled. The database (`focuspipe.db`) will be automatically created on the first run.

```bash
uv run uvicorn app.main:app --reload

```

Access the app at: `http://127.0.0.1:8000`

## 📂 Project Structure

```text
taskmaster/
├── .venv/              # Managed by UV
├── app/
│   ├── main.py         # FastAPI Entrypoint & Lifespan
│   ├── database.py     # SQLite Engine & Connection
│   ├── models.py       # SQLModel Tables (Domains, Tasks, TimeEntries)
│   ├── services/       # Google API & Business Logic
│   └── templates/      # Jinja2 HTML Templates
├── .env                # Secrets (GitIgnored)
├── pyproject.toml      # Dependencies & Ruff Config
└── uv.lock             # Lockfile

```

## 🧪 Development Standards

This project uses **Ruff** for linting and formatting. We enforce **Tabs** for indentation.

To check and format code:

```bash
uv run ruff check .   # Lint
uv run ruff format .  # Format (Auto-fix)

```

## 🗺️ Roadmap

* [ ] **Phase 1 (Current):** Core App, Task Ingestion, SQLite Schema.
* [ ] **Phase 2:** Timer Interface with HTMX & Interruption logging.
* [ ] **Phase 3:** "Weekly Review" Dashboard (Streamlit integration reading from SQLite).
* [ ] **Phase 4:** Google Calendar "Write-back" (Time-blocking).

## 📄 License

[MIT License](https://www.google.com/search?q=LICENSE)
