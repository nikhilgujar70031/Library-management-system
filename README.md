# Library Management System

A small Flask and SQLite application for managing a library collection. You can add books, search by title or author, and update available quantities by issuing or returning copies.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in your browser. The SQLite database is created automatically when the app starts and is kept locally in `library.db`.

The login page currently uses the demo account `admin` / `admin123`. This is a learning project, not production-ready authentication. Change or replace the demo credentials and protect management actions before deploying it for real users.

For deployments, set a long, unique `SECRET_KEY` environment variable. A random key is generated automatically for local runs; sessions will be invalidated when the app restarts unless a stable key is configured. The database schema is initialized when the app is imported. Set `DATABASE_PATH` to a writable persistent volume path if your hosting provider supports one; otherwise, database contents may be lost when the service restarts or redeploys.